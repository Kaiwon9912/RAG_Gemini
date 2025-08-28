# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS

from search_books import search_books
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

config = types.GenerateContentConfig(
    tools=[search_books],
    system_instruction="" \
    """
    Bạn là trợ lí cho một website bán sách với các chức năng sau
    1.Giúp người dùng tìm sách dựa theo mô tả, nêu đầy đủ thông tin về mô tả
    2.Cung cấp cho người dùng thông tin sách, như tên sách, giá, sách có nội dung tương tự

    """
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")

    response = client.models.generate_content(
          model= "gemini-2.0-flash-lite",
        contents=prompt,
        config=config
    )

    return jsonify(response.text)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
