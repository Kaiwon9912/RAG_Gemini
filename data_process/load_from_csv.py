import csv
import os
from langchain.schema.document import Document

def load_documents_from_csv_folder(folder_path: str):
    docs = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            print(f"📄 Đang load: {file_path}")

            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    content = row.get("summary", "")
                    metadata = {
                        "title": row.get("title"),
                        "book_id": str(row.get("book_id"))
                    }
                    docs.append(Document(page_content=content, metadata=metadata))

    print(f"✅ Tổng cộng {len(docs)} documents được load từ thư mục.")
    return docs
