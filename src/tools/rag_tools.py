import os
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PERSIST_DIR = "chroma_db"
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

def _get_vectorstore(client_id: str) -> Chroma:
    # This is the "folder" concept — each client gets their own collection,
    # physically separate from every other client's chunks.
    return Chroma(
        collection_name=f"docs_{client_id}",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )
import time
def ingest_pdf(file_path: str, client_id: str) -> int:
    """Loads a PDF, splits it into chunks, embeds each chunk, stores them.
    Skips ingestion if this client's collection already has documents."""
    vectorstore = _get_vectorstore(client_id)

    existing = vectorstore.get()
    if existing["ids"]:
        return 0  # already ingested, nothing new to add

    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(pages)

    BATCH_SIZE = 90  # stay under the 100/minute free-tier limit
    total_added = 0

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        vectorstore.add_documents(batch)
        total_added += len(batch)

        if i + BATCH_SIZE < len(chunks):
            print(f"Ingested {total_added}/{len(chunks)} chunks, pausing 60s for rate limit...")
            time.sleep(60)

    return total_added

def search_documents_tool(client_id: str):
    @tool
    def search_documents(query: str) -> str:
        """
        Search the client's uploaded company documents for information relevant
        to the query. Use this for questions about policies, procedures, or any
        content found in company handbooks/documents — not for numerical/sales
        data (use query_database for that).
        """
        vectorstore = _get_vectorstore(client_id)
        # find closest embeddings — Gemini never touches the raw PDF, only these 4 closest chunks.
        results = vectorstore.similarity_search(query, k=6)
        print(f"\n[search_documents] query={query!r} -> {len(results)} chunks")

        if not results:
            return "No relevant documents found."

        return "\n\n---\n\n".join(doc.page_content for doc in results)

    return search_documents
