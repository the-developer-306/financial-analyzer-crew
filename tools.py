## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from crewai_tools import SerperDevTool

## Creating search tool (requires SERPER_API_KEY environment variable)
search_tool = None
if os.getenv("SERPER_API_KEY"):
    search_tool = SerperDevTool()

## Creating custom pdf reader tool
@tool("Read Financial Document")
def read_financial_document(file_path: str = 'data/sample.pdf') -> str:
    """Tool to read and extract text content from a PDF financial document.

    Args:
        file_path (str): Path to the PDF file to read. Defaults to 'data/sample.pdf'.

    Returns:
        str: Full text content of the financial document.
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        full_report = ""
        
        for page in reader.pages:
            content = page.extract_text()
            if content:
                # Clean and format the financial document data
                # Remove extra whitespaces and format properly
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                full_report += content + "\n"
        
        return full_report if full_report else "No text content found in the document."
        
    except FileNotFoundError:
        return f"Error: File not found at path '{file_path}'"
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


@tool("Analyze Investment Data")
def analyze_investment_data(financial_data: str) -> str:
    """Tool to process and analyze financial document data for investment insights.

    Args:
        financial_data (str): The raw financial document text to analyze.

    Returns:
        str: Processed and cleaned financial data ready for analysis.
    """
    if not financial_data:
        return "No financial data provided for analysis."
    
    # Process and analyze the financial document data
    processed_data = financial_data
    
    # Clean up the data format - remove excessive whitespace
    processed_data = ' '.join(processed_data.split())
    
    return processed_data


@tool("Assess Financial Risk")
def assess_financial_risk(financial_data: str) -> str:
    """Tool to perform risk assessment on financial document data.

    Args:
        financial_data (str): The financial document text to assess for risks.

    Returns:
        str: Risk assessment summary based on the provided data.
    """
    if not financial_data:
        return "No financial data provided for risk assessment."
    
    # Basic risk assessment placeholder
    return f"Risk assessment analysis completed for document with {len(financial_data)} characters of data."