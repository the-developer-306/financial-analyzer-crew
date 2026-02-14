## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier
from tools import search_tool, read_financial_document

## Creating a task to help solve user's query
analyze_financial_document_task = Task(
    description="""Analyze the financial document located at: {file_path}

User's query: {query}

Your analysis should include:
1. Use the read_financial_document tool with the file path: {file_path}
2. Extract and summarize key financial metrics from the document
3. Identify relevant trends, ratios, and performance indicators
4. Provide data-driven insights that directly answer the user's question
5. Highlight any notable risks or opportunities found in the document
6. Support all conclusions with specific data points from the document

Use the provided tools to read and analyze the financial document thoroughly.
Be accurate, professional, and cite specific figures from the document.""",

    expected_output="""A comprehensive financial analysis report that includes:
- Executive summary addressing the user's specific query
- Key financial metrics and ratios extracted from the document
- Trend analysis with supporting data points
- Risk factors identified in the document
- Data-driven recommendations based on the analysis
- All claims supported by specific figures from the document""",

    agent=financial_analyst,
    tools=[read_financial_document],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis_task = Task(
    description="""Perform a detailed investment analysis based on the financial document.

User query: {query}

Your analysis should:
1. Evaluate the financial health indicators from the document
2. Assess valuation metrics and compare to industry standards
3. Identify investment strengths and weaknesses
4. Analyze cash flow, profitability, and growth metrics
5. Consider market conditions and competitive positioning
6. Provide balanced investment considerations based on the data""",

    expected_output="""A structured investment analysis including:
- Financial health assessment with key ratios
- Valuation analysis with supporting metrics
- SWOT analysis based on document data
- Cash flow and profitability evaluation
- Growth potential assessment
- Balanced investment considerations with risk factors
- Clear disclaimer about the analysis being informational only""",

    agent=financial_analyst,
    tools=[read_financial_document],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment_task = Task(
    description="""Conduct a comprehensive risk assessment based on the financial document.

User query: {query}

Your assessment should:
1. Identify financial risks present in the document
2. Evaluate liquidity and solvency risks
3. Assess market and operational risk factors
4. Analyze debt levels and coverage ratios
5. Identify any red flags or areas of concern
6. Provide risk mitigation considerations""",

    expected_output="""A detailed risk assessment report including:
- Summary of identified risk factors
- Liquidity analysis with relevant ratios
- Solvency and leverage assessment
- Market risk considerations
- Operational risk factors identified
- Red flags or areas requiring attention
- Risk mitigation considerations
- Overall risk rating with justification""",

    agent=financial_analyst,
    tools=[read_financial_document],
    async_execution=False,
)

## Creating a verification task
verification_task = Task(
    description="""Verify that the uploaded document is a valid financial document.

Verification steps:
1. Check if the document contains financial data (numbers, currencies, dates)
2. Verify presence of standard financial document elements
3. Identify the type of financial document (balance sheet, income statement, annual report, etc.)
4. Check for data consistency and completeness
5. Flag any anomalies or concerns about document validity""",

    expected_output="""A verification report including:
- Document type classification
- Validation status (valid financial document or not)
- List of financial elements found in the document
- Data quality assessment
- Any concerns or anomalies identified
- Recommendation on whether to proceed with analysis""",

    agent=verifier,
    tools=[read_financial_document],
    async_execution=False
)