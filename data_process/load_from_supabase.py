from supabase import create_client
from langchain.schema.document import Document
from tqdm import tqdm # Import tqdm để hiển thị thanh tiến trình nếu bạn muốn
import os
from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
def load_documents_from_supabase():

    print("📄 Đang load documents từ Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    all_docs = []
    page_size = 500  # Số bản ghi mỗi lần load
    offset = 0       # Vị trí bắt đầu

    total_rows_in_db = 0
    try:
        count_response = supabase.table("Book").select("*", count="exact", head=True).execute()
        if count_response and count_response.count is not None:
            total_rows_in_db = count_response.count
            print(f"📈 Tổng số bản ghi trong bảng 'Book' trên Supabase: {total_rows_in_db}")
        else:
            print("⚠️ Không thể lấy tổng số bản ghi từ Supabase. Tiếp tục load mà không có tổng số.")
    except Exception as e:
        print(f"❌ Lỗi khi lấy tổng số bản ghi: {e}. Tiếp tục load mà không có tổng số.")

    # Sử dụng tqdm để hiển thị thanh tiến trình nếu total_rows_in_db > 0
    pbar = tqdm(total=total_rows_in_db, unit="docs", desc="Đang tải documents") if total_rows_in_db > 0 else None

    while True:
        try:
            # Lấy một trang dữ liệu sử dụng .range(start, end)
            # end là offset + page_size - 1 vì range là inclusive
            response = supabase.table("Book") \
                               .select("book_id, title, description, summary") \
                               .range(offset, offset + page_size - 1) \
                               .execute()
            
            if response.data:
                # Thêm các bản ghi đã load vào danh sách tổng
                for row_data in response.data:
                    content = row_data.get("summary", "") 
                    metadata = {
                        "title": row_data.get("title"),
                        "book_id": str(row_data.get("book_id")),
                        "description": str(row_data.get("description"))
                    }
                    all_docs.append(Document(page_content=content, metadata=metadata))
                
                # Cập nhật thanh tiến trình
                if pbar:
                    pbar.update(len(response.data))

                # Nếu số bản ghi nhận được ít hơn page_size, nghĩa là đã hết dữ liệu
                if len(response.data) < page_size:
                    break 
                
                # Tăng offset cho lần load tiếp theo
                offset += page_size
            elif response.error:
                print(f"❌ Lỗi khi load dữ liệu từ Supabase: {response.error}")
                break # Thoát vòng lặp nếu có lỗi
            else:
                # Không có dữ liệu và không có lỗi, nghĩa là đã hết dữ liệu
                break

        except Exception as e:
            print(f"❌ Lỗi không mong muốn trong quá trình load: {e}")
            break # Thoát vòng lặp nếu có lỗi ngoại lệ

    if pbar:
        pbar.close() 

    print(f"✅ Tổng cộng {len(all_docs)} documents đã được load từ Supabase.")
    return all_docs

