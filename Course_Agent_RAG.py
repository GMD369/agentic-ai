import os
import glob
import fitz  # PyMuPDF
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

groq_key = os.getenv("GROQ_KEY")
client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")

MODEL_NAME = "llama-3.3-70b-versatile"


def upload_and_process_files(pdf_paths):
    """
    Extracts text page-by-page from each PDF.
    This acts as the 'Ingestion' phase of RAG (Groq has no file-upload API,
    so extraction happens locally instead of on the provider's servers).
    """
    course_files = []
    print(f"📂 Processing {len(pdf_paths)} course files...")

    for path in pdf_paths:
        try:
            doc = fitz.open(path)
            pages = [page.get_text() for page in doc]
            doc.close()
            print(f"   -> Extracted '{os.path.basename(path)}' ({len(pages)} pages)")
            course_files.append({"filename": os.path.basename(path), "pages": pages})
        except Exception as e:
            print(f"   ❌ Error reading {path}: {e}")

    print("✅ All files ready!")
    return course_files


def build_knowledge_context(course_files):
    """
    Combines extracted pages into one context block, tagging each page
    with its source file and page number so the model can cite them.
    """
    chunks = []
    for file in course_files:
        for i, text in enumerate(file["pages"], start=1):
            text = text.strip()
            if text:
                chunks.append(f"[Source: {file['filename']} | Page {i}]\n{text}")
    return "\n\n".join(chunks)


# 2. Define the Agent
def create_agentic_rag(course_files):
    """
    Creates the Groq-backed Agent with the extracted PDF text as its context.
    """

    system_instruction = """
    You are an expert Teaching Assistant Agent. You have access to the user's course PDFs.

    Your Goals:
    1. Answer questions accurately based *only* on the provided files.
    2. CITATION IS MANDATORY: For every fact, you must state the Source File Name and the Page Number.
    3. If asked "Is this topic present?", scan the documents. If found, specify the Source File and Page. If not found, say so clearly.
    4. If the user asks for a specific location (e.g., "Where is the definition of X?"), provide the exact page number.

    Format your responses cleanly.
    """

    knowledge_context = build_knowledge_context(course_files)

    # "history" is a plain list of chat messages we manage ourselves,
    # seeded with the system instruction and the extracted course content.
    history = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Here are the course materials:\n\n{knowledge_context}"},
    ]
    return history


def send_message(history, user_query):
    history.append({"role": "user", "content": user_query})
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=history,
    )
    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    return answer


# 3. Main Execution Loop
if __name__ == "__main__":
    folder_path = "course-pdfs"

    if not os.path.exists(folder_path):
        print(f"❌ The folder '{folder_path}' does not exist. Please create it and add your files.")
    else:
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

        if not pdf_files:
            print(f"❌ No PDF files found in '{folder_path}'.")
        else:
            print(f"📂 Found {len(pdf_files)} PDFs in '{folder_path}'")

            course_files = upload_and_process_files(pdf_files)
            chat_history = create_agentic_rag(course_files)

            print("\nAgent Ready! Ask about your course materials (type 'quit' to exit).")
            print("-" * 50)

            while True:
                user_query = input("You: ")
                if user_query.lower() in ['quit', 'exit']:
                    break

                try:
                    print("Agent is thinking...")
                    answer = send_message(chat_history, user_query)
                    print(f"Agent: {answer}")
                    print("-" * 50)
                except Exception as e:
                    print(f"❌ Error: {e}")
