from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import CSVLoader
import os
import openai
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

os.environ["OPEN_API_KEY"] = ""
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPEN_API_KEY']

##########################################################
#load pdfs
def LoadPDF(path):
    loader = DirectoryLoader(path, glob="**/*.pdf", show_progress=True, loader_cls=PyPDFLoader)
    return loader.load()

pdf_directory="pdf"
loaded_pdfs=LoadPDF(pdf_directory)
##########################################################
def LoadCSV(path):
    loader = CSVLoader(file_path=path, encoding="utf-8", csv_args={'delimiter': ','})
    return loader.load()

csv_directory="csv"
csv_data_list = []

csv_files = [os.path.join(csv_directory, file) for file in os.listdir(csv_directory) if file.endswith(".csv")]
#tqdm show progress bar
for csv_file in tqdm(csv_files):
    csv_data = LoadCSV(csv_file)
    csv_data_list.append(csv_data)

#######################################################
#LOAD Directory inside another directory
def load_csv_directory(directory_path):
    csv_data_list = []
    
    # Go through all general directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                # print(f"Loading {csv_file_path}...")
                
                # Carga el archivo CSV utilizando CSVLoader
                csv_data = LoadCSV(csv_file_path)
                csv_data_list.append(csv_data)
    
    return csv_data_list

general_directory = "fifa_wc_2018"

# Load CSV from the subdirectories 
load_csv_directory(general_directory)
############################################################

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splitted = text_splitter.split_documents(loaded_pdfs)
########################################################
# embeddings = OpenAIEmbeddings()
# vectorstore = Chroma.from_documents(loaded_pdfs, embeddings)

