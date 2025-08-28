import pandas as pd
import time
from google import genai
from google.genai import types
from search_books import search_books 
import pandas as pd
import random
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_question_from_description(description):
    instruction = f"""
    Bạn là một trợ lý AI chuyên tạo câu hỏi dựa trên nội dung mô tả sách.
    Hãy tạo duy nhất **một câu hỏi duy nhất** mà người đọc có thể hỏi nếu họ quan tâm đến cuốn sách này.
    Tránh lặp lại nguyên văn mô tả, hãy diễn đạt tự nhiên.
    Chỉ trả về đúng một câu hỏi, không thêm bất kỳ giải thích nào.

    Mô tả sách:
    {description}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=instruction),
        contents="Tạo câu hỏi từ mô tả trên.",
    )

    return response.text.strip()

def score_rag_output(query, context, answer):
    instruction = """
    Bạn là AI đánh giá câu trả lời RAG. Trả về điểm số từ 0 đến 5 cho từng tiêu chí:
    1. Relevance Score
    2. Context Coverage
    3. Factual Correctness
    4. Fluency & Clarity
    Và tổng điểm Overall Quality (0–10)

    Trả về JSON với định dạng:
    {
        "relevance": 4,
        "coverage": 5,
        "factual": 5,
        "fluency": 4,
        "overall": 9
    }
    """
    content = f"""Câu hỏi: {query}

Trả lời:
{answer}
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=instruction),
        contents=content
    )
    import json, re
    try:
        json_str = re.search(r"\{.*\}", response.text.strip(), re.DOTALL).group(0)
        return json.loads(json_str)
    except Exception as e:
        return {
            "relevance": 0,
            "coverage": 0,
            "factual": 0,
            "fluency": 0,
            "overall": 0,
            "error": str(e)
        }

def run_batch_evaluation(books: list, output_excel="rag_evaluation.xlsx"):
    results = []

    for book in books:
        description = book["description"]
        title = book.get("title", "Không tên")

        
        question = generate_question_from_description(description)

        start = time.time()
        rag_result = search_books(question)
        duration = round(time.time() - start, 2)

       
        results.append({
            "Book Title": title,
            "Generated Question": question,
            "RAG Answer": rag_result["answer"],
            "Book IDs": ", ".join(rag_result.get("book_ids", [])),
            "Response Time (s)": duration,
           
        })

    df = pd.DataFrame(results)
    df.to_excel(output_excel, index=False)
    print(f"✅ Kết quả đã lưu vào {output_excel}")
    results = []

    for book in books:
        description = book["description"]
        title = book.get("title", "Không tên")

       
        question = generate_question_from_description(description)

        start = time.time()
        rag_result = search_books(question)
        duration = round(time.time() - start, 2)

        # Lưu kết quả
        results.append({
            "Book Title": title,
            "Generated Question": question,
            "RAG Answer": rag_result["answer"],
            "Book IDs": ", ".join(rag_result.get("book_ids", [])),
            "Response Time (s)": duration,
          
        })

    df = pd.DataFrame(results)
    df.to_excel(output_excel, index=False)
    print(f"✅ Kết quả đã lưu vào {output_excel}")
    results = []

    for book in book_list:
        title = book.get("title", "Không rõ")
        description = book.get("description", "")
        question = generate_question_from_description(description)

        start = time.time()
        result = search_books(question)
        elapsed = round(time.time() - start, 2)
        answer = result.get("answer", "")
        eval_scores = score_rag_output(question, description, answer)

        results.append({
                "Title": title,
                "Question": question,
                "Answer": answer,
                "Relevance": eval_scores.get("relevance", 0),
                "Coverage": eval_scores.get("coverage", 0),
                "Factual": eval_scores.get("factual", 0),
                "Fluency": eval_scores.get("fluency", 0),
                "Overall": eval_scores.get("overall", 0),
                "Time (s)": elapsed,
            })

    df = pd.DataFrame(results)
    df.to_excel(output_excel, index=False)
    print(f"✅ Đã lưu kết quả vào {output_excel}")

def summarize_results(filename="rag_evaluation.xlsx"):
    df = pd.read_excel(filename)
    print("📊 Tổng số câu hỏi:", len(df))
    print("🎯 Điểm trung bình:")
    print(df[["Relevance", "Coverage", "Factual", "Fluency", "Overall"]].mean())
    print("✅ Số câu Overall > 8:", (df["Overall"] > 8).sum())
    print("❌ Số câu Overall < 5:", (df["Overall"] < 5).sum())

def load_random_books_from_csv(filename, n=10):
    df = pd.read_csv(filename)
    df = df.dropna(subset=["title", "description"])  

    if len(df) < n:
        print(f"⚠️ File chỉ có {len(df)} sách.")
        n = len(df)

    sampled = df.sample(n=n, random_state=42)  
    books = sampled[["title", "description"]].to_dict(orient="records")
    return books
