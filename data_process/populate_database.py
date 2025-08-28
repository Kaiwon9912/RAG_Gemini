import argparse
from langchain_text_splitters import CharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
from tqdm import tqdm
from load_from_supabase import load_documents_from_supabase
from load_from_csv import load_documents_from_csv_folder
import os
from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "book_vectors_test"


def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_supabase(chunks)


def load_documents():
    return load_documents_from_supabase()


def split_documents(documents: list[Document]) -> list[Document]:
    chunk_map = {}
    print(f"Tổng số tài liệu đầu vào (documents): {len(documents)}")
    for doc in documents:
        uid = doc.metadata.get("book_id") or doc.metadata.get("book_id") or "unknown_uid"
        title = doc.metadata.get("title") or "unknown_title"

        # Split the text content directly by the comma
        parts = doc.page_content.split(",")
        
        for part in parts:
            content = part.strip()
            if not content:
                continue

            if content in chunk_map:
                existing_doc = chunk_map[content]
                existing_doc.metadata["uids"].add(uid)
                existing_doc.metadata["titles"].add(title)
            else:
                chunk_map[content] = Document(
                    page_content=content,
                    metadata={
                        "uids": set([uid]),
                        "titles": set([title]),
                    }
                )

    final_chunks = []
    for doc in chunk_map.values():
        doc.metadata["uids"] = list(doc.metadata["uids"])
        doc.metadata["titles"] = list(doc.metadata["titles"])
        final_chunks.append(doc)

    return final_chunks
def calculate_chunk_ids(chunks: list[Document]):
    current_book_id = None
    chunk_index = 0
    

    for chunk in chunks:
        book_id = chunk.metadata.get("book_id")
        if book_id == current_book_id:
            chunk_index += 1
        else:
            chunk_index = 0
            current_book_id = book_id

      
        chunk_id = f"{book_id}:{chunk_index}"
        chunk.metadata["chunk_id"] = chunk_id  # for Supabase

    return chunks

def add_to_supabase(chunks: list[Document]):
    embedding_fn = get_embedding_function()
    supabase = get_supabase_client()

    vectorstore = SupabaseVectorStore(
        client=supabase,
        table_name=TABLE_NAME,
        embedding=embedding_fn
    )



    print(f"👉 New chunks to add: {len(chunks)}")

    if not chunks:
        print("✅ No new chunks to add.")
        return

    for i in tqdm(range(0, len(chunks), 10), desc="📦 Uploading"):
        batch = chunks[i:i + 10]
        vectorstore.add_documents(batch)


if __name__ == "__main__":
    main()
