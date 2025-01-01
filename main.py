import os
from dotenv import load_dotenv
from cf import CloudflareWorkerClient
from ragops import load_documents_from_gcs, split_documents, create_voyage_embeddings

load_dotenv()  # take environment variables from .env.

# Initialize the client
client = CloudflareWorkerClient(
    worker_url=os.getenv("CF_WORKER_URL"),
    api_token=os.getenv("CF_API_KEY"),
    embedding_function=create_voyage_embeddings
)

# Load and process documents (using your existing functions)
documents = load_documents_from_gcs(
    bucket_name=os.getenv("SOURCE_BUCKET_NAME"),
    prefix=os.getenv("SOURCE_PREFIX"),
    extension_filter=".md",
    project_id=os.getenv("GCP_PROJECT_ID")
)

# Split documents
chunks = split_documents(documents)

# Add to vector store
result = client.add_documents(chunks)
