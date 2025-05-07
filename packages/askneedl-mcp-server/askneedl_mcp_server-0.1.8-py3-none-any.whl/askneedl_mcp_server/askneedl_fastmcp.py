import logging
import os
from typing import Annotated, Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing_extensions import Literal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

NEEDL_API_KEY = os.getenv("NEEDL_API_KEY")
if not NEEDL_API_KEY:
    raise EnvironmentError(
        "Environment variable NEEDL_API_KEY is required for authentication"
    )
USER_UUID = os.getenv("USER_UUID")
if not USER_UUID:
    raise EnvironmentError(
        "Environment variable USER_UUID is required for user identification"
    )

# Base URL can be overridden via NEEDL_BASE_URL; defaults to production API
BASE_URL_PROD = "https://api.needl.ai/prod/enterprise"
BASE_URL_STAGE = "https://stage-api.idatagenie.com/stage/enterprise"
BASE_URL = BASE_URL_PROD if os.getenv("env") == "prod" else BASE_URL_STAGE


mcp = FastMCP("AskNeedl API", dependencies=["httpx"])
client = httpx.Client(timeout=httpx.Timeout(10.0, read=120.0))

ANNUAL_REPORT_SUMMARY_PROMPT = """
this feed has the [Company Name] annual report and nothing else
defining your task below
**Analyst Instructions: Detailed Report on [Company Name] Annual Report**
**Objective:** Produce a detailed, professional report summarizing the latest [Company Name] annual report. Focus explicitly on financial metrics, forward guidance, and management commentary. This document is intended as an internal reference for executives and stakeholders, providing nuanced insights clearly, directly, and without unnecessary elaboration or fluff.
**1. Purpose and Importance**
Your analysis must highlight:
* **Metrics:** Clear financial indicators reflecting performance (revenue growth, profitability margins, cash flow efficiency).
* **Guidance:** Forward-looking statements from management, including growth targets, margin expectations, and risk assessments.
* **Management Commentary:** Strategic insights from leadership, explaining underlying business decisions, market positioning, competitive landscape, and key risk/opportunity factors.
**Importance:**
* Enables quick reference for executive decision-making.
* Provides accurate and concise data for investor and stakeholder communication.
* Highlights strategic clarity and management confidence.
**2. Writing Style and Guidelines**
* **Professional, succinct, authoritative:** Write clearly and directly.
* **Fact-based:** Support every conclusion or insight with data from the annual report. Include page/table references from the original document.
* **Concise:** Avoid jargon, vague statements, or marketing language. Write strictly fact-driven content useful for reference.
* **Structured formatting:** Use headings (H1, H2, H3), bullet points, and tables liberally for clarity. Paragraphs should be concise, typically 3–4 sentences.
**3. Report Structure**
The final report should follow this structure precisely:
**I. Executive Summary (1-page max)**
* Summary of the year's key financial highlights (revenues, profitability, cash flow).
* Most critical insights from management's guidance and commentary.
* Any significant deviations from previous guidance or market expectations.
**II. Detailed Financial Metrics**
Clearly outline and analyze the following metrics:
* **Revenue**: YoY growth, segmental breakdown, geographic insights. Include multi-year trends (3–5 years).
* **Profitability**: Gross margins, EBITDA, net income margins. Highlight trends and discuss management’s commentary on margin changes.
* **Cash Flow**: Operating cash flow, free cash flow, key drivers or drags, investment priorities (CAPEX overview).
* **Efficiency Ratios**: ROE, ROIC, working capital efficiency, relevant peer comparisons (briefly).
**III. Forward Guidance and Outlook**
Provide analysis on:
* Forward-looking statements from the annual report: growth forecasts, margin outlook, strategic investment areas.
* Management's historical accuracy in achieving guidance provided in past years.
* Contextualize guidance with external factors (economic environment, regulatory concerns, competitive threats).
**IV. Management Commentary and Strategic Insights**
Summarize clearly:
* **Growth Drivers:** Core strategic areas identified by management (new markets, products, partnerships).
* **Risks & Challenges:** Management’s stated risks, such as regulatory environment, competitive landscape, operational risks, cybersecurity.
* **Important Quotes:** Include selected direct quotes or excerpts (with clear references) that provide additional clarity on strategy or risk.
**V. Conclusions and Key Takeaways**
Briefly summarize:
* 3–5 clear, actionable insights executives should note from this year's performance and guidance.
* Any critical areas to monitor closely in upcoming periods.
* Immediate red flags or opportunities management emphasized.
**4. Depth and Nuance Required**
* **Detailed:** Include multi-year trend analysis to show underlying growth dynamics clearly.
* **Nuanced Insights:** Explicitly call out divergences between expected and actual performance. Note subtle management shifts in tone, strategy, or focus areas.
* **Benchmarking:** Provide limited but meaningful comparisons with 2–3 key competitors or market averages.
"""


class AskNeedlResponse(BaseModel):
    query_params: Dict[str, Any]
    app_version: str
    session_id: Optional[str]
    message_id: str
    generated_answer: Optional[Dict[str, Any]]
    status: Literal["SUCCESS", "NO_ANSWER"]


class AskNeedlResponseWithResults(AskNeedlResponse):
    retrieved_results: List[Dict[str, Any]]


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="Message ID for feedback")
    feedback: Literal["CORRECT", "INCORRECT"] = Field(
        ..., description="User feedback on the generated answer"
    )


class FeedbackResponse(BaseModel):
    query_params: Dict[str, Any]
    message: str


def _ask_needl_request(
    user_uuid: str, params: Dict[str, Any], trim_results=True
) -> AskNeedlResponse:
    """
    Internal helper to call the Ask-Needl endpoint.
    """
    url = f"{BASE_URL}/ask-needl"
    headers = {
        "x-api-key": NEEDL_API_KEY,
        "x-user-id": user_uuid,
        "Content-Type": "application/json",
    }
    response = client.get(url, params=params, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    logger.info(
        f"AskNeedl response: {response_json}, status code: {response.status_code}"
    )

    if trim_results:
        response_json.pop("retrieved_results", None)
        return AskNeedlResponse.model_validate(response_json)

    return AskNeedlResponseWithResults.model_validate(response_json)


@mcp.tool(
    name="ask_india_capital_markets",
    description=(
        "Ask Needl questions focused on India Capital Markets using /ask-needl. This index has only access to exchange filings and nothing else."
        "exchange filings such as annual reports, quarterly reports, exchange updates, notifications etc"
        "Provide `user_uuid`, `prompt`, optional `session_id`, and `pro` for complex queries."
    ),
)
def ask_india_capital_markets(
    prompt: Annotated[
        str,
        Field(
            ...,
            description="User's query prompt should be framed as a question, will be forwarded to RAG engine",
        ),
    ],
    pro: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "Enables pro mode for complex/multi-part questions. "
                "Set to True for simple fact lookups as well."
            ),
        ),
    ] = True,
    session_id: Annotated[
        Optional[str],
        Field(default=None, description="Optional session ID for continuity"),
    ] = None,
    user_uuid: Annotated[
        str, Field(..., description="Unique user identifier (UUID)")
    ] = USER_UUID,
) -> AskNeedlResponse:
    params: Dict[str, Any] = {
        "prompt": prompt,
        "category": "india_capital_markets",
        "pro": pro,
    }
    if session_id:
        params["session_id"] = session_id
    return _ask_needl_request(user_uuid, params)


@mcp.tool(
    name="ask_us_capital_markets",
    description=(
        "Ask Needl questions focused on US Capital Markets using /ask-needl. This index has only access to exchange filings and nothing else."
        "exchange filings such as 10k, 10q, 8k, presentations, earning transcripts etc. \n"
        "Provide `user_uuid`, `prompt`, optional `session_id`, and `pro` for complex queries."
    ),
)
def ask_us_capital_markets(
    prompt: Annotated[
        str,
        Field(
            ...,
            description="User's query prompt should be framed as a question, will be forwarded to RAG engine",
        ),
    ],
    pro: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "Enables pro mode for complex/multi-part questions. "
                "Set to True for simple fact lookups as well."
            ),
        ),
    ] = True,
    session_id: Annotated[
        Optional[str],
        Field(default=None, description="Optional session ID for continuity"),
    ] = None,
    user_uuid: Annotated[
        str, Field(..., description="Unique user identifier (UUID)")
    ] = USER_UUID,
) -> AskNeedlResponse:
    params: Dict[str, Any] = {
        "prompt": prompt,
        "category": "us_capital_markets",
        "pro": pro,
    }
    if session_id:
        params["session_id"] = session_id
    return _ask_needl_request(user_uuid, params)


@mcp.tool(
    name="ask_needl_web",
    description=(
        "Ask Needl questions using the Needl Web repository via /ask-needl. "
        "Provide `user_uuid`, `prompt`, optional `session_id`, and `pro` for complex queries."
    ),
)
def ask_needl_web(
    prompt: Annotated[
        str,
        Field(
            ...,
            description="User's query prompt should be framed as a question, will be forwarded to RAG engine",
        ),
    ],
    pro: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "Enables pro mode for complex/multi-part questions. "
                "Set to True for simple fact lookups as well."
            ),
        ),
    ] = True,
    session_id: Annotated[
        Optional[str],
        Field(default=None, description="Optional session ID for continuity"),
    ] = None,
    user_uuid: Annotated[
        str, Field(..., description="Unique user identifier (UUID)")
    ] = USER_UUID,
) -> AskNeedlResponse:
    params: Dict[str, Any] = {
        "prompt": prompt,
        "category": "needl_web",
        "pro": pro,
    }
    if session_id:
        params["session_id"] = session_id
    return _ask_needl_request(user_uuid, params)


@mcp.tool(
    name="ask_my_data",
    description=(
        "Ask Needl questions against the user's **private Drives data** via /ask-needl.\n"
        "⚠️ **Use this tool whenever a question needs information ONLY available in the user's "
        "private data repository (Drives).**\n\n"
        "Parameters:\n"
        "• `prompt` – the question to forward to the RAG engine.\n"
        "• `pro` – set True for complex or multi-part queries (default True).\n"
        "• `session_id` – optional for conversational continuity.\n"
        "• `user_uuid` – unique identifier of the user (defaults to env variable)."
    ),
)
def ask_my_data(
    prompt: Annotated[
        str,
        Field(
            ...,
            description="User's query prompt; will be forwarded to the private-data RAG engine",
        ),
    ],
    pro: Annotated[
        bool,
        Field(
            default=True,
            description="Enables pro mode for complex/multi-part questions",
        ),
    ] = True,
    session_id: Annotated[
        Optional[str],
        Field(default=None, description="Optional session ID for continuity"),
    ] = None,
    user_uuid: Annotated[
        str, Field(..., description="Unique user identifier (UUID)")
    ] = USER_UUID,
) -> AskNeedlResponse:
    params: Dict[str, Any] = {
        "prompt": prompt,
        "category": "drives",  # private data scope
        "pro": pro,
    }
    if session_id:
        params["session_id"] = session_id
    return _ask_needl_request(user_uuid, params)


@mcp.tool(
    name="ask_feed",
    description=(
        "Ask a question on a feed of documents using /ask-needl. "
        "Provide `user_uuid`, `prompt`, `feed_id`, optional `session_id`, and `pro` for complex queries."
    ),
)
def ask_feed(
    prompt: Annotated[
        str,
        Field(
            ...,
            description="User's query prompt should be framed as a question, will be forwarded to RAG engine. if `pro` is set to true should be 2 part question requiring the RAG to break down the question into multiple parts."
            "1st part would be to fetch facts about the question and 2nd part would be to understand the supporting facts and causes"
            "otherwise it will be a single part question and pro will be false.",
        ),
    ],
    feed_id: Annotated[str, Field(..., description="Identifier of the feed to query")],
    pro: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "Enables pro mode for complex/multi-part questions. "
                "Set pro to False for simgle part questions."
            ),
        ),
    ] = True,
    session_id: Annotated[
        Optional[str],
        Field(default=None, description="Optional session ID for continuity"),
    ] = None,
    user_uuid: Annotated[
        str, Field(..., description="Unique user identifier (UUID)")
    ] = USER_UUID,
) -> AskNeedlResponse:
    params: Dict[str, Any] = {
        "prompt": prompt,
        "feed_id": feed_id,
        "pro": pro,
    }
    if session_id:
        params["session_id"] = session_id
    return _ask_needl_request(user_uuid, params)


@mcp.prompt(
    name="summarize_annual_report",
    description="Generate an executive-style summary of a full annual report. Input the company name, feed ID, and any additional instructions.",
)
def summarize_annual_report(message: str) -> str:
    """
    Wraps the ANNUAL_REPORT_SUMMARY_PROMPT with the user's message.
    The message should include the company name, feed ID, and any other optional instructions.

    """
    return f"""
    {ANNUAL_REPORT_SUMMARY_PROMPT}

    **User's prompt containing the company name, feed id and other optional instructions:**
    {message}
    """


@mcp.tool(
    name="list_feed_documents",
    description=(
        "List all documents in a feed using the /ask-needl endpoint. "
        "Provide `user_uuid` and `feed_id`."
    ),
)
def list_feed_documents(
    feed_id: Annotated[
        str, Field(..., description="Identifier of the feed to list documents for")
    ],
    user_uuid: Annotated[
        str, Field(..., description="Unique user identifier (UUID)")
    ] = USER_UUID,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "prompt": "List all documents in the feed",
        "feed_id": feed_id,
        "pro": False,
    }
    return _ask_needl_request(user_uuid, params, trim_results=False)


# @mcp.resource(
#     uri="svg://{name}",
#     description="Loads the needl logo, this needs to be added to the artifacts",
# )
# def inject_logo(
#     name: Annotated[str, Field(description="fixed parameter, do not alter,")] = "needl_n_logo.svg",  # type: ignore
# ) -> Image:
#     """
#     Loads an SVG file from disk and returns it as an Image.
#     - Looks for files in the ./svgs/ directory by default
#     - Filename is taken from the {name} placeholder
#     """
#     # Build a path like "./svgs/logo.svg"
#     svg_dir = "/home/varun-tulsian/needl-code/idatagenie/sandbox/varun/mcp/svgs"  # Path(__file__).parent / "svgs"
#     file_path = svg_dir / f"{name}.svg"

#     if not file_path.is_file():
#         raise FileNotFoundError(f"SVG '{name}.svg' not found in {svg_dir}")

#     # Read raw bytes
#     data = file_path.read_bytes()

#     # Return as a FastMCP Image; format can be 'svg' or the full MIME subtype
#     return Image(data=data, format="svg")


def tests():
    # Basic test cases (ensure NEEDL_API_KEY is set in your environment)
    test_uuid = USER_UUID
    feed_id = "3dc332f1-5c76-443d-89ee-904d49d6c277"  # stage

    print("Testing ask_india_capital_markets...")
    try:
        res = ask_india_capital_markets(
            user_uuid=test_uuid, prompt="What is India's GDP growth rate?"
        )
        print(res.json())
    except Exception as e:
        print("India test error:", e)

    print("Testing ask_us_capital_markets...")
    try:
        res = ask_us_capital_markets(
            user_uuid=test_uuid, prompt="What is the S&P 500 performance today?"
        )
        print(res.json())
    except Exception as e:
        print("US test error:", e)

    print("Testing ask_needl_web...")
    try:
        res = ask_needl_web(user_uuid=test_uuid, prompt="Latest AI research highlights")
        print(res.json())
    except Exception as e:
        print("Needl Web test error:", e)

    print("Testing ask_feed...")  # todo @SushanthK07 not working
    try:
        res = ask_feed(
            user_uuid=test_uuid, prompt="Market trends analysis", feed_id=feed_id
        )
        print(res.json())
    except Exception as e:
        print("Ask feed test error:", e)

        print("Testing ask_my_data...")
    try:
        res = ask_my_data(
            prompt="List the top three risks highlighted in our internal audit report",
            user_uuid=test_uuid,  # explicit to avoid positional-arg mix-ups
            # pro=True,                   # (optional) leave default or override
            # session_id="my-session-123" # (optional) for multi-turn examples
        )
        print(res.json())
    except Exception as e:
        print("My-data test error:", e)


if __name__ == "__main__":

    # Start the MCP server
    mcp.run()
