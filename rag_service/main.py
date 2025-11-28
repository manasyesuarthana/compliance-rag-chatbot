import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import glob

app = FastAPI(title="Regulatory RAG (Gemini Powered)")

# Configuration
PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Global Singleton
vector_db = None

def get_vector_db():
    global vector_db
    if not vector_db:
        print("--> [*] Initializing Local Embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vector_db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
        print("--> [*] Vector DB Loaded.")
    return vector_db

class QueryRequest(BaseModel):
    question: str

class Source(BaseModel):
    source: str
    page: int
    context: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Source]

@app.on_event("startup")
async def startup():
    global vector_db
    print("--> Starting RAG Engine...")
    db = get_vector_db()
    
    # check if the DB is empty by trying to get 1 item
    existing_records = db.get(limit=1)
    
    if len(existing_records['ids']) == 0:
        print("--> [-] Brain is empty. Auto-ingesting default documents from /app/data...")
        
        pdf_files = glob.glob("./data/*.pdf")
        
        if not pdf_files:
            print("--> [!] No PDFs found in /app/data. Waiting for manual ingestion.")
            return

        for pdf_path in pdf_files:
            try:
                print(f"--> Ingesting: {pdf_path}")
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = splitter.split_documents(docs)
                
                if chunks:
                    db.add_documents(chunks)
                    db.persist()
                    print(f"--> [*] Indexed {len(chunks)} chunks from {pdf_path}")
            except Exception as e:
                print(f"--> [X] Failed to ingest {pdf_path}: {e}")
                
        print("--> Auto-ingestion complete. System Ready.")
    else:
        print("--> [*] Brain is already populated. Skipping auto-ingestion.")

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        loader = PyPDFLoader(temp_file)
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        db = get_vector_db()
        db.add_documents(chunks)
        db.persist()
        
        os.remove(temp_file)
        return {"status": "success", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not set")

    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        convert_system_message_to_human=True,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    template = """Answer the question based ONLY on the following context. 
    If you cannot answer the question based on the context, say "I don't know".
    
    Context:
    {context}
    
    Question: {question}
    """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    result = qa_chain.invoke({"query": request.question})
    
    citations = []
    for doc in result['source_documents']:
        citations.append(Source(
            source=os.path.basename(doc.metadata.get('source', 'unknown')),
            page=doc.metadata.get('page', 0),
            context=doc.page_content[:200] + "..."
        ))

    return QueryResponse(answer=result['result'], citations=citations)