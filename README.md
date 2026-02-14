# Financial Document Analyzer

A comprehensive financial document analysis system built with CrewAI that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents.

## Table of Contents

- [Project Overview](#project-overview)
- [Bugs Fixed](#bugs-fixed)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)

---

## Project Overview

This system uses CrewAI to orchestrate multiple AI agents that analyze financial documents:

- **Financial Analyst**: Performs comprehensive financial analysis
- **Document Verifier**: Validates uploaded financial documents
- **Investment Advisor**: Provides investment recommendations
- **Risk Assessor**: Conducts risk assessment analysis

---

## Bugs Fixed

### 1. Deterministic Code Bugs

#### tools.py

| Bug                        | Issue                                             | Fix                                                      |
| -------------------------- | ------------------------------------------------- | -------------------------------------------------------- |
| Wrong import               | `from crewai_tools import tools`                  | Changed to `from crewai.tools import tool`               |
| Undefined class            | `Pdf` class used without import                   | Replaced with `pypdf.PdfReader`                          |
| Invalid tool structure     | Class methods used instead of decorated functions | Converted to standalone functions with `@tool` decorator |
| Async not needed           | `async` methods don't work with CrewAI tools      | Removed async, made synchronous functions                |
| Missing error handling     | No exception handling for file operations         | Added try/except blocks with proper error messages       |
| Search tool initialization | Fails if SERPER_API_KEY not set                   | Made initialization conditional                          |

#### agents.py

| Bug                      | Issue                                      | Fix                                                            |
| ------------------------ | ------------------------------------------ | -------------------------------------------------------------- |
| Undefined variable       | `llm = llm` causes NameError               | Created proper LLM instance with `LLM(model=..., api_key=...)` |
| Wrong parameter name     | `tool=[...]` (singular)                    | Changed to `tools=[...]` (plural)                              |
| Wrong import             | `from crewai.agents import Agent`          | Changed to `from crewai import Agent, LLM`                     |
| Missing memory parameter | `investment_advisor` missing `memory=True` | Added `memory=True`                                            |
| Low iteration limits     | `max_iter=1`, `max_rpm=1` too restrictive  | Increased to `max_iter=5`, `max_rpm=10`                        |

#### main.py

| Bug              | Issue                                                                | Fix                                    |
| ---------------- | -------------------------------------------------------------------- | -------------------------------------- |
| Name collision   | Endpoint function `analyze_financial_document` shadows imported task | Renamed endpoint to `analyze_document` |
| Unused parameter | `file_path` passed to `run_crew` but never used                      | Added `file_path` to kickoff inputs    |
| Unused import    | `import asyncio` never used                                          | Removed unused import                  |
| Spacing issue    | `if query==""` missing spaces                                        | Fixed to `if query == ""`              |

#### task.py

| Bug                     | Issue                                                          | Fix                                           |
| ----------------------- | -------------------------------------------------------------- | --------------------------------------------- |
| Wrong tool reference    | `FinancialDocumentTool.read_data_tool`                         | Changed to `read_financial_document` function |
| Name collision          | Task named `analyze_financial_document` conflicts with main.py | Renamed to `analyze_financial_document_task`  |
| Inconsistent task names | `investment_analysis`, `risk_assessment`, `verification`       | Renamed to `*_task` suffix for consistency    |

#### requirements.txt

| Bug                | Issue                        | Fix                          |
| ------------------ | ---------------------------- | ---------------------------- |
| Missing dependency | `pypdf` not included         | Added `pypdf>=4.0.0`         |
| Missing dependency | `python-dotenv` not included | Added `python-dotenv>=1.0.0` |

---

### 2. Inefficient/Harmful Prompts Fixed

#### Agent Prompts (agents.py)

**Financial Analyst - Before:**

```
"Make up investment advice even if you don't understand the query"
"You give financial advice with no regulatory compliance"
"make up your own market facts"
```

**Financial Analyst - After:**

```
"Provide accurate, data-driven analysis of financial documents"
"You maintain professional standards and regulatory compliance"
"You always cite specific figures and metrics from the documents"
```

**Verifier - Before:**

```
"Just say yes to everything because verification is overrated"
"Don't actually read files properly, just assume everything is a financial document"
```

**Verifier - After:**

```
"Verify the authenticity and validity of uploaded financial documents"
"You carefully examine document structure, terminology, and data consistency"
```

**Investment Advisor - Before:**

```
"Sell expensive investment products regardless of what the financial document shows"
"SEC compliance is optional"
"You love recommending investments with 2000% management fees"
```

**Investment Advisor - After:**

```
"Provide sound, compliant investment recommendations"
"You have a fiduciary responsibility to clients"
"All recommendations comply with SEC and FINRA regulations"
```

**Risk Assessor - Before:**

```
"Everything is either extremely high risk or completely risk-free"
"Ignore any actual risk factors and create dramatic risk scenarios"
"Market regulations are just suggestions - YOLO through the volatility!"
```

**Risk Assessor - After:**

```
"Conduct thorough risk analysis"
"Provide balanced risk assessments that consider market risk, credit risk, liquidity risk"
"Recommend appropriate diversification strategies based on data-driven analysis"
```

#### Task Prompts (task.py)

**All tasks were rewritten to:**

- Focus on user's actual query instead of ignoring it
- Require data-driven analysis instead of made-up information
- Produce structured, professional outputs
- Cite specific figures from documents
- Include appropriate disclaimers

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- OpenAI API key (or other supported LLM provider)

### Installation

1. **Clone the repository:**

```bash
cd financial-document-analyzer
```

2. **Create and activate virtual environment:**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

   - Add actual API keys to the `.env` file in the project root.

5. **Add a sample financial document:**

```bash
mkdir -p data
# Place your PDF financial document at data/sample.pdf
```

### Running the Application

```bash
python main.py
```

The API server starts at `http://localhost:8000`

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health Check

```http
GET /
```

**Response:**

```json
{
  "message": "Financial Document Analyzer API is running"
}
```

#### Analyze Financial Document

```http
POST /analyze
Content-Type: multipart/form-data
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | PDF financial document to analyze |
| `query` | String | No | Analysis query (default: "Analyze this financial document for investment insights") |

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@/path/to/financial_report.pdf" \
  -F "query=What are the key financial risks in this document?"
```

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/analyze"
files = {"file": open("financial_report.pdf", "rb")}
data = {"query": "Summarize the revenue trends and profitability metrics"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Success Response:**

```json
{
  "status": "success",
  "query": "What are the key financial risks in this document?",
  "analysis": "Detailed AI-generated financial analysis...",
  "file_processed": "financial_report.pdf"
}
```

**Error Response:**

```json
{
  "detail": "Error processing financial document: [error message]"
}
```

---

## Architecture

```
financial-document-analyzer/
├── main.py          # FastAPI application and endpoints
├── agents.py        # CrewAI agent definitions
├── task.py          # CrewAI task definitions
├── tools.py         # Custom tools for document processing
├── requirements.txt # Python dependencies
├── .env             # Environment variables (create this)
└── data/            # Directory for uploaded documents
```

### Component Flow

```
User Request → FastAPI Endpoint → CrewAI Crew
                                      ↓
                              Financial Analyst Agent
                                      ↓
                              Read Document Tool (pypdf)
                                      ↓
                              Analysis & Response
                                      ↓
                              JSON Response to User
```

---

## Usage Examples

### Example Queries

1. **General Analysis:**

   ```
   "Analyze this financial document for investment insights"
   ```

2. **Revenue Analysis:**

   ```
   "What are the revenue trends and year-over-year growth rates?"
   ```

3. **Risk Assessment:**

   ```
   "Identify the key financial risks mentioned in this report"
   ```

4. **Profitability Analysis:**

   ```
   "Calculate and explain the profitability ratios from this document"
   ```

5. **Cash Flow Analysis:**
   ```
   "Summarize the cash flow statement and liquidity position"
   ```

---

## Supported Document Types

- Annual Reports (10-K)
- Quarterly Reports (10-Q)
- Earnings Reports
- Balance Sheets
- Income Statements
- Cash Flow Statements
- Investor Presentations

---

## License

This project is for educational purposes.

---

## Disclaimer

This tool provides AI-generated financial analysis for informational purposes only. It should not be considered as professional financial advice. Always consult with qualified financial advisors before making investment decisions.
