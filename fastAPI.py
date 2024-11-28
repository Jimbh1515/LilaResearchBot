from fastapi import FastAPI
import os 
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


load_dotenv() 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=GEMINI_API_KEY )
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)


client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))


DB_NAME = "coach_db"
COLLECTION_NAME = "coach_collection"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "coach-index-1"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from your Vue app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/question/")
async def get_ai_answer(question:str):

    client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))


    #DB_NAME = "test_db"
    #COLLECTION_NAME = "test_collection_pdf"
    #ATLAS_VECTOR_SEARCH_INDEX_NAME = "test-index-pdf"

    #MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

    #vector_store = MongoDBAtlasVectorSearch(
        #collection=MONGODB_COLLECTION,
        #embedding=embeddings,
        #index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
       # relevance_score_fn="cosine",
    #)

    retriever = vector_store.as_retriever()

    chain = RetrievalQA.from_chain_type(
        llm = llm_model,
        retriever = retriever,
        chain_type = "stuff"
    )

    ai_response = chain.invoke(question)
    client.close()
    
    return ai_response["result"]
