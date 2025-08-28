import re 
from supabase import create_client
from get_embedding_function import get_embedding_function
from generate_queries import generate_related_queries

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_2")),


def relevant_check(query: str, book_context: str) -> float:
    print(book_context)
    instruction = f"""
    Bạn là một trợ lý đánh giá độ liên quan.
    Hãy đánh giá mức độ liên quan của ngữ cảnh sách: "{book_context}" với câu hỏi/yêu cầu: "{query}".
    Trả về một điểm số từ 0.0 đến 1.0, trong đó 1.0 là rất liên quan và 0.0 là không liên quan.
    Nếu không thể xác định được độ liên quan, hãy trả về 0.0.
    Chỉ trả về điểm số, không thêm bất kỳ văn bản nào khác.
    """
    response = client.models.generate_content(
        model= "gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=instruction),
        contents=f"Context: {book_context}\nQuery: {query}\nRelevance Score:",
    )
    
    response_text = response.text.strip()
    
    try:
        match = re.search(r'\d+\.?\d*', response_text)
        if match:
            score = float(match.group(0))
            return max(0.0, min(1.0, score))
        else:
            print(f"Warning: relevant_check could not find a number in response: '{response_text}'")
            return 0.0
    except ValueError:
        print(f"Warning: relevant_check returned unparseable response after regex: '{response_text}'")
        return 0.0