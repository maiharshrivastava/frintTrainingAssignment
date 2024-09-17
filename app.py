from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
api_key: str = os.getenv("GOOGLE_API_KEY")

# Initialize Google Generative AI components for embeddings and conversational model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=api_key)
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, api_key=api_key)

# FastAPI app instance
app = FastAPI()

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Welcome to the PDF Question-Answering API!"}

def get_pdf_text(pdf_docs: List[UploadFile]) -> str:
    text: str = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf.file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text: str) -> List[str]:
    text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks: List[str] = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks: List[str]) -> None:
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain() -> Any:
    prompt_template: str = """ Answer the question as detailed as possible from the provided context. If the answer is not available in the context, say, "Answer is not available in the context." Do not provide incorrect information.

    Context:
    {context}
    
    Question:
    {question}

    Answer: """
    prompt: PromptTemplate = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain: Any = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question: str) -> str:
    try:
        # Load the FAISS index with dangerous deserialization enabled
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        chain = get_conversational_chain()
        response: Dict[str, Any] = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error loading vector store: {e}")

@app.post("/process-pdf/")
async def process_pdf(files: List[UploadFile] = File(...)) -> Dict[str, str]:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    try:
        raw_text: str = get_pdf_text(files)
        text_chunks: List[str] = get_text_chunks(raw_text)
        get_vector_store(text_chunks)
        return {"status": "success", "message": "PDFs processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF files: {e}")

@app.get("/ask-question/")
async def ask_question(
    question: str = Query(..., example="What is the summary of the document?")
) -> Dict[str, str]:
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    try:
        response: str = user_input(question)
        return {"question": question, "answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {e}")
