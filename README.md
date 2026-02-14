# Financial Document Analyzer

A comprehensive financial document analysis system built with CrewAI that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents.

## Table of Contents

- [Project Overview](#project-overview)
- [Bonus Features](#bonus-features)
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

## Bonus Features

This project includes two major enterprise-level features:

### Queue Worker Model (Celery + Redis)

**Purpose**: Handle concurrent requests efficiently without blocking the API server.

**Benefits**:

- **Asynchronous Processing**: Submit documents and get results later
- **Scalability**: Process multiple documents concurrently
- **Reliability**: Failed jobs don't crash the server
- **Job Tracking**: Monitor job status in real-time
- **Background Processing**: API responds immediately while analysis runs in the background

**Technology Stack**:

- **Celery**: Distributed task queue for Python
- **Redis**: In-memory message broker for fast job queuing

### Database Integration (SQLAlchemy + SQLite/PostgreSQL)

**Purpose**: Persist analysis results and track usage history.

**Benefits**:

- **Historical Data**: Store all analyses for future reference
- **Analytics**: Track usage statistics and performance metrics
- **Audit Trail**: Complete record of all analysis requests
- **Query History**: Retrieve past results without re-processing
- **User Activity Tracking**: Monitor usage patterns and success rates

**Database Schema**:

- **analysis_requests**: Track job submissions and status
- **analysis_results**: Store completed analysis results
- **user_activity**: Log usage statistics and metrics

**Supported Databases**:

- **SQLite** (default): Zero-configuration, file-based database
- **PostgreSQL**: Production-ready relational database (optional)

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

| Bug                | Issue                                                                | Fix                                    |
| ------------------ | -------------------------------------------------------------------- | -------------------------------------- |
| Name collision     | Endpoint function `analyze_financial_document` shadows imported task | Renamed endpoint to `analyze_document` |
| Unused parameter   | `file_path` passed to `run_crew` but never used                      | Added `file_path` to kickoff inputs    |
| Unused import      | `import asyncio` never used                                          | Removed unused import                  |
| Spacing issue      | `if query==""` missing spaces                                        | Fixed to `if query == ""`              |
| Host address issue | `host =` "0.0.0.0"                                                   | Fixed to `host = "127.0.0.1"`          |

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
- DeepSeek API key (see [Why DeepSeek?](#why-deepseek) section below)
- **Optional (for async processing)**: Redis server (for Celery queue worker)

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

   Create a `.env` file in the project root with the following:

   ```env
   # DeepSeek API Configuration
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DEEPSEEK_MODEL=deepseek-chat
   DEEPSEEK_BASE_URL=https://api.deepseek.com

   # Embeddings Configuration (Optional)
   EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2

   # Optional: Search Tool API Key
   SERPER_API_KEY=your_serper_api_key_here

   # Redis Configuration (for Celery queue worker)
   REDIS_URL=redis://localhost:6379/0

   # Database Configuration
   # SQLite (default - no setup needed)
   DATABASE_URL=sqlite:///./financial_analyzer.db

   # PostgreSQL (uncomment and configure if you want to use PostgreSQL)
   # DATABASE_URL=postgresql://username:password@localhost:5432/financial_analyzer
   ```

   **Note:** Get your DeepSeek API key from [https://platform.deepseek.com](https://platform.deepseek.com)

5. **Add a sample financial document:**

```bash
mkdir -p data
# Place your PDF financial document at data/sample.pdf
```

6. **Install Redis (Optional - for async processing):**

   **Windows:**
   - Download from [Redis Windows](https://github.com/microsoftarchive/redis/releases)
   - Or use Docker: `docker run -d -p 6379:6379 redis:latest`

   **Linux/Mac:**

   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server

   # Mac with Homebrew
   brew install redis
   brew services start redis
   ```

### Running the Application

#### Basic Mode (Synchronous Processing)

Start the FastAPI server:

```bash
python main.py
```

The API server starts at `http://localhost:8000`

**Features Available**:

- Synchronous document analysis (`/analyze`)
- Database storage of results
- History and statistics endpoints
- Async processing disabled

#### Advanced Mode (With Queue Worker)

**Step 1**: Start Redis server (if not already running)

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

**Step 2**: Start the Celery worker in a separate terminal

```bash
celery -A celery_worker worker --loglevel=info
```

**Step 3**: Start the FastAPI server in another terminal

```bash
python main.py
```

**Features Available**:

- Synchronous document analysis (`/analyze`)
- Asynchronous document analysis (`/analyze/async`)
- Job status tracking (`/status/{job_id}`)
- Result retrieval (`/result/{job_id}`)
- Database storage of results
- History and statistics endpoints
- Concurrent request handling

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
  "message": "Financial Document Analyzer API is running",
  "version": "2.0.0",
  "features": {
    "async_processing": true,
    "database": true,
    "sync_processing": true
  }
}
```

#### Analyze Financial Document (Synchronous)

```http
POST /analyze
Content-Type: multipart/form-data
```

**Description**: Synchronous endpoint that blocks until analysis is complete.

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

**Success Response:**

```json
{
  "status": "success",
  "query": "What are the key financial risks in this document?",
  "analysis": "Detailed AI-generated financial analysis...",
  "file_processed": "financial_report.pdf"
}
```

#### Analyze Financial Document (Asynchronous)

```http
POST /analyze/async
Content-Type: multipart/form-data
```

**Description**: Asynchronous endpoint that returns immediately with a job ID. Requires Redis and Celery worker.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | PDF financial document to analyze |
| `query` | String | No | Analysis query (default: "Analyze this financial document for investment insights") |

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/analyze/async" \
  -F "file=@/path/to/financial_report.pdf" \
  -F "query=What are the key financial risks in this document?"
```

**Success Response:**

```json
{
  "status": "submitted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document submitted for analysis. Use /status/{job_id} to check progress.",
  "filename": "financial_report.pdf",
  "query": "What are the key financial risks in this document?"
}
```

#### Get Job Status

```http
GET /status/{job_id}
```

**Description**: Check the status of an async analysis job.

**Example Request:**

```bash
curl -X GET "http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000"
```

**Response (Processing):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "filename": "financial_report.pdf",
  "query": "What are the key financial risks in this document?",
  "created_at": "2026-02-15T10:30:00",
  "updated_at": "2026-02-15T10:30:15"
}
```

**Response (Completed):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "filename": "financial_report.pdf",
  "query": "What are the key financial risks in this document?",
  "created_at": "2026-02-15T10:30:00",
  "updated_at": "2026-02-15T10:32:45",
  "completed_at": "2026-02-15T10:32:45",
  "message": "Analysis completed. Use /result/{job_id} to retrieve the result."
}
```

#### Get Job Result

```http
GET /result/{job_id}
```

**Description**: Retrieve the analysis result for a completed job.

**Example Request:**

```bash
curl -X GET "http://localhost:8000/result/550e8400-e29b-41d4-a716-446655440000"
```

**Success Response:**

```json
{
  "status": "success",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "financial_report.pdf",
  "query": "What are the key financial risks in this document?",
  "analysis": "Detailed AI-generated financial analysis...",
  "processing_time": 145.67,
  "created_at": "2026-02-15T10:32:45"
}
```

#### Get Analysis History

```http
GET /history?limit=10&offset=0
```

**Description**: Retrieve paginated history of all completed analyses.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | Integer | 10 | Number of records (1-100) |
| `offset` | Integer | 0 | Number of records to skip |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/history?limit=5&offset=0"
```

**Success Response:**

```json
{
  "total": 42,
  "limit": 5,
  "offset": 0,
  "results": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "financial_report.pdf",
      "query": "What are the key financial risks?",
      "processing_time": 145.67,
      "created_at": "2026-02-15T10:32:45"
    }
  ]
}
```

#### Get Statistics

```http
GET /stats
```

**Description**: Get usage statistics and analytics.

**Example Request:**

```bash
curl -X GET "http://localhost:8000/stats"
```

**Success Response:**

```json
{
  "total_analyses_completed": 42,
  "total_requests": 50,
  "status_breakdown": {
    "pending": 2,
    "processing": 3,
    "completed": 42,
    "failed": 3
  },
  "average_processing_time_seconds": 138.45,
  "success_rate_percentage": 84.0,
  "celery_enabled": true
}
```

---

## Why DeepSeek?

### LLM Provider Change

This project has been **intentionally configured to use DeepSeek** as the LLM provider instead of OpenAI for the following reasons:

1. **Cost-Effective**: DeepSeek offers competitive pricing for API calls, making it more economical for financial document analysis at scale.
2. **High Performance**: DeepSeek's models provide excellent reasoning capabilities suitable for complex financial analysis tasks.
3. **OpenAI-Compatible API**: The API structure is similar to OpenAI's, making it easy to integrate with CrewAI.

### Embeddings Model Change

The project uses **Sentence Transformers** from HuggingFace instead of OpenAI embeddings:

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (default)
- **Benefits**:
  - **Free and Open Source**: No API costs for embeddings
  - **Local Processing**: Embeddings are generated locally without external API calls
  - **Privacy**: Document content stays on your machine during embedding generation
  - **Fast**: Efficient model optimized for semantic similarity tasks
- **Integration**: Seamlessly integrated with ChromaDB, which CrewAI uses internally for memory and embeddings

### Configuration Location

- **LLM Configuration**: See [agents.py](agents.py) - Lines 10-14
- **Embeddings Configuration**: See [embeddings_config.py](embeddings_config.py)

---

## Architecture

```
financial-document-analyzer/
├── main.py              # FastAPI application and endpoints
├── agents.py            # CrewAI agent definitions
├── task.py              # CrewAI task definitions
├── tools.py             # Custom tools for document processing
├── database.py          # Database models and configuration (NEW)
├── celery_config.py     # Celery configuration (NEW)
├── celery_worker.py     # Celery task definitions (NEW)
├── embeddings_config.py # Embeddings configuration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── data/                # Directory for uploaded documents
└── outputs/             # Output directory
```

### Component Flow

**Synchronous Processing:**

```
User Request → POST /analyze → FastAPI
                                  ↓
                          Save File to Disk
                                  ↓
                          CrewAI Crew (run_crew)
                                  ↓
                          Financial Analyst Agent
                                  ↓
                          Read Document Tool (pypdf)
                                  ↓
                          LLM Analysis (DeepSeek API)
                                  ↓
                          Return Result → User
```

**Asynchronous Processing with Queue:**

```
User Request → POST /analyze/async → FastAPI
                                        ↓
                                  Save to Database
                                        ↓
                                  Queue Job (Redis)
                                        ↓
                                  Return job_id → User

Redis Queue ← Celery Worker (Background)
      ↓              ↓
  Job Queue    Process Job
                     ↓
              CrewAI Crew
                     ↓
              Financial Analyst
                     ↓
              LLM Analysis
                     ↓
              Save Result to DB
                     ↓
              Update Job Status

User → GET /status/{job_id} → Check Status
User → GET /result/{job_id} → Retrieve Result
```

### Database Schema

**analysis_requests**

- Tracks all analysis job submissions
- Fields: job_id, filename, query, status, timestamps, error_message

**analysis_results**

- Stores completed analysis results
- Fields: job_id, filename, query, analysis, processing_time, created_at

**user_activity**

- Logs user activity and usage patterns
- Fields: job_id, user_ip, file_size, query_length, success, timestamp

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

### Python Usage Examples

#### Synchronous Analysis

```python
import requests

def analyze_document_sync(file_path, query):
    """Synchronous analysis - blocks until complete"""
    url = "http://localhost:8000/analyze"

    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"query": query}
        response = requests.post(url, files=files, data=data)

    result = response.json()
    print(f"Status: {result['status']}")
    print(f"Analysis: {result['analysis']}")
    return result

# Usage
result = analyze_document_sync(
    "financial_report.pdf",
    "What are the key financial risks?"
)
```

#### Asynchronous Analysis with Polling

```python
import requests
import time

def analyze_document_async(file_path, query):
    """Asynchronous analysis - submit and poll for results"""

    # Step 1: Submit document for analysis
    url = "http://localhost:8000/analyze/async"
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"query": query}
        response = requests.post(url, files=files, data=data)

    result = response.json()
    job_id = result["job_id"]
    print(f"Job submitted: {job_id}")

    # Step 2: Poll for completion
    status_url = f"http://localhost:8000/status/{job_id}"

    while True:
        status_response = requests.get(status_url)
        status_data = status_response.json()

        print(f"Status: {status_data['status']}")

        if status_data["status"] == "completed":
            break
        elif status_data["status"] == "failed":
            print(f"Error: {status_data.get('error')}")
            return None

        time.sleep(2)  # Wait 2 seconds before checking again

    # Step 3: Retrieve result
    result_url = f"http://localhost:8000/result/{job_id}"
    result_response = requests.get(result_url)
    result_data = result_response.json()

    print(f"Analysis complete!")
    print(f"Processing time: {result_data['processing_time']} seconds")
    print(f"Analysis: {result_data['analysis']}")

    return result_data

# Usage
result = analyze_document_async(
    "financial_report.pdf",
    "Analyze revenue trends and profitability"
)
```

#### Get Analysis History

```python
import requests

def get_history(limit=10):
    """Retrieve analysis history"""
    url = f"http://localhost:8000/history?limit={limit}&offset=0"
    response = requests.get(url)
    data = response.json()

    print(f"Total analyses: {data['total']}")
    for result in data['results']:
        print(f"- {result['filename']}: {result['query']}")

    return data

# Usage
history = get_history(limit=5)
```

#### Get Statistics

```python
import requests

def get_stats():
    """Get usage statistics"""
    url = "http://localhost:8000/stats"
    response = requests.get(url)
    stats = response.json()

    print(f"Total analyses: {stats['total_analyses_completed']}")
    print(f"Success rate: {stats['success_rate_percentage']}%")
    print(f"Average time: {stats['average_processing_time_seconds']}s")
    print(f"Celery enabled: {stats['celery_enabled']}")

    return stats

# Usage
stats = get_stats()
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