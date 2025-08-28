
from supabase import create_client
from generate_queries import generate_related_queries

from google import genai
from google.genai import types
from bm25_search  import bm25_filter
from relevant_check import relevant_check
import re 

from dotenv import load_dotenv
import os
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_2"))




def get_supabase_client():
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def search_books(query: str, embedding_function) -> dict:
    supabase = get_supabase_client()
    all_queries = [query] 
    all_results = []

    for q in all_queries:
        query_embedding = embedding_function.embed_query(q) 
        response = supabase.rpc("match_documents_AI", {
            "k": 5,
            "query_embedding": query_embedding
        }).execute()

        for doc in response.data or []:
            all_results.append(doc)

    if not all_results:
        return {"answer": "❌ No relevant documents found.", "book_ids": []}

    scored_books = []
    for doc in all_results:
        meta = doc.get("metadata")
        if not meta:
            continue

        book_context = f"""Tên sách: {meta.get('title', 'No title')},

        Mô tả: {bm25_filter(query, meta.get('description') or 'Không có mô tả')}

        """

        book_context = bm25_filter(query, book_context)
        relevance_score = relevant_check(query, book_context)
        
        if relevance_score > 0.5: 
            scored_books.append({"doc": doc, "score": relevance_score})

    if not scored_books:
        return {"answer": "❌ Không tìm thấy sách phù hợp yêu cầu.", "book_ids": []}

    re_ranked_books = sorted(scored_books, key=lambda x: x["score"], reverse=True)
    relevant_books = [item["doc"] for item in re_ranked_books]

    context_text = "\n\n---\n\n".join([
        f"""Tên sách: {meta.get('title', 'No title')}
         Mô tả: {bm25_filter(query, meta.get('description') or 'Không có mô tả')} """
        for doc in relevant_books
        if (meta := doc.get("metadata"))
    ])
    

    instruction = f"""
    Bạn là một trợ lý thân thiện, thông minh, chuyên gợi ý và thảo luận về sách. Người dùng vừa hỏi:
    Dưới đây là danh sách một số cuốn sách có thể phù hợp với yêu cầu. Hãy trò chuyện một cách tự nhiên, gợi ý các lựa chọn, đưa nhận xét ngắn gọn, và nếu có thể hãy rủ người dùng đọc thử.
    Danh sách sách phù hợp:
        {context_text}

        Hướng dẫn:
        - Trò chuyện như đang thảo luận thật với người dùng, thân thiện nhưng súc tích.
        - Nêu tên sách và mô tả vắn tắt vì sao sách đó đáng đọc theo nội dung người dùng hỏi.
        - Nếu sách không liên quan tới yêu cầu / câu người dùng thì bỏ qua.
        - Tuyệt đối không thêm nội dung không có trong dữ liệu sách.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=instruction),
        contents=query,
    )


    answer = response.text.strip()
  

    return {
        "answer": answer,
        "book_ids": [doc['metadata'].get('book_id') for doc in relevant_books if doc.get("metadata")]
    }