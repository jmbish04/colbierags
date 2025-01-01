import os
import io
# import json
from dotenv import load_dotenv
# from langchain_core.documents import Document
from langchain.text_splitter import MarkdownTextSplitter
# from langchain_google_community import GCSDirectoryLoader, GCSFileLoader
from langchain.document_loaders import TextLoader
from langchain_voyageai import VoyageAIEmbeddings
from google.cloud import storage

load_dotenv()  # take environment variables from .env.

# Access the GOOGLE_APPLICATION_CREDENTIALS variable
google_app_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Set the environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_app_credentials

# Initialize GCS client once (outside the function)
storage_client = storage.Client(project=os.getenv("GCP_PROJECT_ID"))


def load_documents_from_gcs(bucket_name, prefix, extension_filter="*.md"):
    """Loads documents from a GCS bucket, filtering by file extension."""

    try:
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)

        documents = []
        for blob in blobs:
            if blob.name.lower().endswith(extension_filter.lower()):
                # Use in-memory stream (optional)
                with io.BytesIO() as in_memory_file:
                    blob.download_to_file(in_memory_file)
                    in_memory_file.seek(0)

                    # Load using TextLoader (adapt if needed)
                    loader = TextLoader(in_memory_file)
                    docs = loader.load()

                    for doc in docs:
                        doc.metadata['source'] = f"gs://{bucket_name}/{blob.name}"
                    documents.extend(docs)

    except Exception as e:
        print(f"Error loading documents from GCS: {e}")
        # Handle the error appropriately (e.g., return an empty list or raise an exception)

    return documents


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    print(f" Splitting docs")
    text_splitter = MarkdownTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def create_voyage_embeddings(model_name: str = "voyage-law-2"):
    """Creates embeddings using the VoyageAIEmbeddings model.

    Args:
        model_name (str, optional): The name of the Voyage model to use. Defaults to "voyage-law-2".

    Returns:
        VoyageAIEmbeddings: An instance of VoyageAIEmbeddings configured with the specified model.
    """
    print(f" Building voyager embeddings")
    if os.getenv("VOYAGE_API_KEY") is None:
        raise ValueError("Voyage AI API key must be provided.")

    return VoyageAIEmbeddings(api_key=os.getenv("VOYAGE_API_KEY"), model=model_name)


