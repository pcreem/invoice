from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')

# ✅ OCR.Space API 金鑰（請自行替換為有效的）
OCR_SPACE_API_KEY = 'K82170038988957'

@app.route('/')
def index():
    # 回傳前端主頁
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 檢查是否有檔案
    if 'file' not in request.files:
        return jsonify({'error': '未找到檔案'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未選擇檔案'}), 400

    # ✅ 準備 OCR API 資料
    payload = {
        'apikey': OCR_SPACE_API_KEY,
        'language': 'cht',  # 使用正確繁體中文語言代碼
        'isOverlayRequired': False
    }

    # ✅ 正確指定 file: (檔名, 檔案物件, 類型)
    files = {
        'file': (file.filename, file, file.content_type)
    }

    # 發送 POST 請求到 OCR.Space API
    response = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
    result = response.json()

    # ✅ 錯誤處理
    if result.get('OCRExitCode') != 1 or not result.get('ParsedResults'):
        return jsonify({'error': result.get('ErrorMessage', 'OCR 解析失敗')}), 500

    # ✅ 提取文字
    text = result['ParsedResults'][0].get('ParsedText', '')
    return jsonify({'text': text})

if __name__ == '__main__':
    # 啟動伺服器
    app.run(debug=True)
