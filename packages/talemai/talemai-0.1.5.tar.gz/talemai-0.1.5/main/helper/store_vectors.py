from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from main.helper.pdf import save_online_pdf
from main.helper.creditionals import read_db_config
from main.helper.spinner import spinner
import os
import click

async def store_vectors(pdf_url, collection_name, namespace):

    db_config = read_db_config()
    pdf_path = save_online_pdf(pdf_url)

    # Error handling if file is not found
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    pdf_loader = PyPDFLoader(pdf_path)  
    documents = pdf_loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)


    spinner()

    vectorstore = AstraDBVectorStore(
        collection_name=collection_name,
        embedding=embeddings,
        api_endpoint=db_config.api_endpoint,
        token=db_config.token,
        namespace=namespace,
    )
  
    vectorstore.add_documents(documents=docs)

    os.remove(pdf_path)

    click.echo(click.style("Stored vector embeddings ✅", fg="green"))