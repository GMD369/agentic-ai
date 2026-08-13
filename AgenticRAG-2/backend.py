import os
import glob
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "llama-3.3-70b-versatile"


def extract_pdf_text(path):
    """
    Extracts text page-by-page from a single PDF, tagging each page
    with its source filename and page number (for citations).
    """
    doc = fitz.open(path)
    chunks = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            chunks.append(f"[Source: {os.path.basename(path)} | Page {i}]\n{text}")
    doc.close()
    return "\n\n".join(chunks)


def upload_org_docs(folder_path="company_docs"):
    """
    Extracts text from all PDFs in the organization's folder.
    Returns the combined, citation-tagged text (Groq has no file-upload
    API, so extraction happens locally instead of on the provider's servers).
    """
    if not os.path.exists(folder_path):
        return ""

    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    print(f"📂 Found {len(pdf_files)} company docs. Extracting text...")

    texts = []
    for path in pdf_files:
        try:
            texts.append(extract_pdf_text(path))
        except Exception as e:
            print(f"❌ Error reading {path}: {e}")

    return "\n\n".join(texts)

def scrape_web_content(url):
    """
    Scrapes the text content from a given URL for the agent to read.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    

        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:50000] # Limit to 50k chars to avoid token overload if site is huge
    except Exception as e:
        return f"Error scraping website: {str(e)}"

def analyze_project_feasibility(api_key, org_docs_text, client_content):
    """
    The core Agentic function.
    org_docs_text: combined, citation-tagged text extracted from company PDFs
    client_content: text content (from URL scrape or extracted client PDF)
    """
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)

    # Define the Agent's Persona
    system_instruction = """
    You are a Senior Project Bid Manager & Technical Evaluator for our company.
    
    Your Task:
    1. Read our Company Documents (provided in context) to understand our skills, past projects, and tech stack.
    2. Analyze the Client's Project Requirement (provided as text or file).
    3. Determine if we are capable of delivering this project.
    
    Output Format:
    ## 🎯 Feasibility Decision: [YES / NO / MAYBE]
    
    ### Reasoning
    Why can or can't we do it? (Cite specific past projects or skills from our docs that match).
    
    ### Gap Analysis
    - **Matches:** What requirements do we meet perfectly?
    - **Missing:** What requirements are we missing or have no experience in?
    
    ### Tender/Govt Check
    Is this a government tender? Any specific strict compliances mentioned?
    
    ### Estimated Timeline & Budget
    (If mentioned in client doc, state it. If not, estimate based on similar past projects in our docs).
    
    ### Next Steps
    Draft a polite response or internal note on how to proceed.
    """

    user_message = (
        f"COMPANY DOCUMENTS:\n{org_docs_text}\n\n"
        f"CLIENT PROJECT DESCRIPTION / WEBPAGE CONTENT:\n{client_content}\n\n"
        "Above is our company knowledge followed by the client's project requirement. "
        "Analyze the client requirement against our company docs."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content