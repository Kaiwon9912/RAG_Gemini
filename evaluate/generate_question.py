import pandas as pd
import random
from tqdm import tqdm
from together import Together
import os
# ---- Cấu hình ----
API_KEY = os.getenv("TOGETHER_API_KEY")

INPUT_CSV = "11481_Books.csv"
OUTPUT_CSV = "questions.csv"
NUM_SAMPLES = 100  # 🔁 Số lượng câu hỏi muốn sinh

# ---- Khởi tạo Together client ----
client = Together(api_key=API_KEY)

# ---- Hàm xây dựng prompt từ thông tin sách ----
def build_prompt(book):
    return (
        f"""Dưới đây là tên và mô tả về một cuốn sách:

- Tên sách: {book.get('title', '')}
- Mô tả: {book.get('description', '')}

Hãy tạo một câu hỏi tự nhiên bằng tiếng Việt, mà người dùng có thể hỏi chatbot để tìm ra cuốn sách này. 
Câu hỏi không được lặp nguyên văn tiêu đề hoặc mô tả, mà nên mô tả đúng nhu cầu tìm kiếm nội dung, thể loại, cảm hứng, hoặc mục đích đọc sách.
Câu hỏi ngắn gọn, không quá giống chi tiết về miêu tả cuốn sách
"""
    )

# ---- Bước 1: Đọc toàn bộ CSV ----
df_all = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

# ---- Bước 2: Lấy ngẫu nhiên N dòng ----
df_sampled = df_all.sample(n=NUM_SAMPLES, random_state=42).reset_index(drop=True)

# ---- Bước 3: Sinh câu hỏi từ AI ----
questions = []
for i, row in tqdm(df_sampled.iterrows(), total=len(df_sampled), desc="🤖 Đang tạo câu hỏi"):
    try:
        prompt = build_prompt(row)
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        question = response.choices[0].message.content.strip().replace("\n", " ")
        questions.append(question)
    except Exception as e:
        print(f"❌ Lỗi dòng {i}: {e}")
        questions.append("")

# ---- Bước 4: Xuất file CSV chứa title + question ----
df_result = pd.DataFrame({
    "Title": df_sampled["title"],
    "Question": questions
})
df_result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"\n✅ Đã tạo {len(questions)} câu hỏi ngẫu nhiên và lưu vào: {OUTPUT_CSV}")
