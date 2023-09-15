from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import CSVLoader
import os
import openai
from dotenv import load_dotenv
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
import uvicorn
import nest_asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel


#directories
pdf_directory="./pdf"
csv_directory="./csv"
general_directory = "./fifa_wc_2018"
chroma_directory = "./chroma"
#arrays
csv_data_list = []
csv_files = [os.path.join(csv_directory, file) for file in os.listdir(csv_directory) if file.endswith(".csv")]
all_data=[]
record=[]

#API_KEY
load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")


#LOAD METHODS
#pdfs
def LoadPDF(path):
    loader = DirectoryLoader(path, glob="**/*.pdf", show_progress=True, loader_cls=PyPDFLoader)
    return loader.load()

#csvs from directory
def LoadCSV(path):
    loader = CSVLoader(file_path=path, encoding="utf-8", csv_args={'delimiter': ','})
    return loader.load()

#csvs from subdirectory and its sub- subdirectory
def load_csv_directory(directory_path):
    
    # Go through all general directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                # print(f"Loading {csv_file_path}...")
                
                csv_data = LoadCSV(csv_file_path)
                # csv_data_list.append(csv_data)
    
    return csv_data




#SPLIT METHOD
def Split(pdfs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    splitted = text_splitter.split_documents(pdfs)
    return splitted



#LOADING
loaded_pdfs=LoadPDF(pdf_directory)

#tqdm show progress bar
for csv_file in tqdm(csv_files):
    csv_data1 = LoadCSV(csv_file)
    csv_data_list.append(csv_data1)

csv_data2=load_csv_directory(general_directory)
csv_data_list.append(csv_data2)


#SPLITTING
splitted=Split(loaded_pdfs)


#VECTORSTORAGE
all_data.extend(splitted)
all_data.extend(csv_data1)
all_data.extend(csv_data2)
embeddings = OpenAIEmbeddings()
#obtain
vectorstore = Chroma.from_documents(documents=all_data,embedding=embeddings,persist_directory=chroma_directory)
#save
vector=Chroma(persist_directory=chroma_directory, embedding_function=embeddings)



#CONVERSATIONAL AGENT
agent = ConversationalRetrievalChain.from_llm(
    llm = OpenAI(),
    retriever=vector.as_retriever()
)


def Chat(msg,record):
    answer = agent({"question": msg, "chat_history": record})
    record.append((msg,answer["answer"]))

    return answer["answer"]

Chat("Quien gano la copa mundial de futbol del 2010?",record)


#FAST API
app = FastAPI()
origins = ["null"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class prompt(BaseModel):
    user_prompt : str


@app.post("/prompt")
async def Post_prompt(prompt : prompt):
    return {"response" : Chat(prompt.user_prompt,record)}

nest_asyncio.apply()
uvicorn.run(app,port=8855)
