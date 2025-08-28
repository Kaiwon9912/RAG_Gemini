from supabase import create_client
from langchain.schema.document import Document
import os
from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL =  os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
def load_documents_from_supabase():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("Book_1").select("book_id", "title", "description","category", "price", "author", "published_year", "pages", "summary").execute()
    docs = []

    
    for row in response.data:
        content = row["summary"]

        metadata = {
            "title": row.get("title"),
            "published_year": row.get("published_year"),
            "pages": row.get("pages"),
            "category": row.get("category"),
            "price": row.get("price"),
            "author": row.get("author"),
            "description": row.get("description"),
            "id": str(row["book_id"])
        }
        docs.append(Document(page_content=content, metadata=metadata))

    return docs
