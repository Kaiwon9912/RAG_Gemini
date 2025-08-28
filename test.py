# test.py
import csv
import time
from search_books import search_books # Giữ nguyên import search_books
from get_embedding_function import get_embedding_function # <- Import để tải mô hình

# Define a delay between API calls to prevent overload
API_CALL_DELAY_SECONDS = 20.0

# --- TẢI MÔ HÌNH EMBEDDING MỘT LẦN DUY NHẤT TẠI ĐÂY ---
print("Đang tải mô hình embedding. Vui lòng chờ...")
embedding_model_instance = get_embedding_function()
print("Đã tải xong mô hình embedding.")
# --- KẾT THÚC TẢI MỘ HÌNH ---


# Đọc câu hỏi từ file CSV
input_file = 'questions.csv'
output_file = 'result_2.csv'

questions = []
with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        question = row.get('Question')
        if question:
            questions.append(question)

# Ghi kết quả
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['Question', 'Answer', 'Latency'])
    writer.writeheader()

    for i, question in enumerate(questions):
        start_time = time.time()
 
        result = search_books(question, embedding_model_instance) 
        end_time = time.time()
        latency = round(end_time - start_time, 2)

        writer.writerow({
            'Question': question,
            'Answer': result.get('answer', 'Không có câu trả lời'),
            'Latency': latency
        })

        if i < len(questions) - 1:
            print(f"Pausing for {API_CALL_DELAY_SECONDS} seconds to prevent API overload...")
            time.sleep(API_CALL_DELAY_SECONDS)

print(f"✅ Đã lưu kết quả vào {output_file}")