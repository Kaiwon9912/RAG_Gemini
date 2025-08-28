import pandas as pd
from tqdm import tqdm
from together import Together
import argparse

# ---- 1. Nhận tham số từ dòng lệnh ----
parser = argparse.ArgumentParser(description="Tóm tắt sách bằng từ khóa.")
parser.add_argument("--api_key", type=str, required=True, help="API key của Together")
parser.add_argument("--input", type=str, default="books.csv", help="Đường dẫn file CSV đầu vào")
parser.add_argument("--output", type=str, default="books_output.csv", help="Đường dẫn file CSV đầu ra")
args = parser.parse_args()

# ---- 2. Khởi tạo Together client ----
client = Together(api_key=args.api_key)

# ---- 3. Hàm tạo prompt ----
def build_prompt(description):
    return (
        "Tóm tắt nội dung bằng các từ khóa chính. "
        "Bao gồm cả các từ khóa có xuất hiện trong văn bản, và những từ khóa có thể được suy luận từ ý nghĩa nội dung. "
        "Không giải thích, không mô tả. Chỉ liệt kê các từ khóa ngắn gọn, phân cách bằng dấu phẩy. "
        "Giữ nguyên các trích dẫn hoặc cụm từ đặc biệt (nếu có).\n"
        f"Sau đây là nội dung:\n{description}"
    )

# ---- 4. Đọc dữ liệu ----
df = pd.read_csv(args.input, encoding="utf-8-sig")

# ---- 5. Tóm tắt từng dòng ----
summaries = []
for i, row in tqdm(df.iterrows(), total=len(df), desc="📘 Đang tóm tắt mô tả"):
    desc = str(row.get("description", ""))
    try:
        prompt = build_prompt(desc)
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=256
        )
        content = response.choices[0].message.content.strip().replace("\n", " ")
        summaries.append(content)
    except Exception as e:
        print(f"❌ Lỗi dòng {i}: {e}")
        summaries.append("")

# ---- 6. Ghi kết quả ----
df["summary"] = summaries
df.to_csv(args.output, index=False, encoding="utf-8-sig")

print(f"✅ Hoàn tất! Đã lưu vào {args.output}")
