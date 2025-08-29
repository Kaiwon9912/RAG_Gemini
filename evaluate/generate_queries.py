# generate_queries.py


import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()


client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def generate_related_queries(query: str) -> list[str]:
    instruction = """
    Bạn là một trợ lý AI chuyên tạo các truy vấn tìm kiếm tương tự.
    Tạo 3 truy vấn khác nhau về mặt diễn đạt nhưng giữ nguyên ý nghĩa.
    Chỉ trả về danh sách, mỗi truy vấn một dòng, không thêm lời giải thích.
    """
    response = client.models.generate_content(
          model= "gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=instruction),
        contents=query,
    )
    queries = response.text.strip().split('\n')
    cleaned_queries = [re.sub(r'^\d+[\.\)]\s*', '', q).strip() for q in queries if q.strip()]
    return cleaned_queries[:3]
