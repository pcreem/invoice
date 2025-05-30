from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')

OCR_SPACE_API_KEY = 'K82170038988957'  # 請替換為你的 OCR.Space 金鑰

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '未找到檔案'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未選擇檔案'}), 400

    payload = {
        'apikey': OCR_SPACE_API_KEY,
        'language': 'cht',
        'isOverlayRequired': False
    }

    files = {
        'file': (file.filename, file, file.content_type)
    }

    response = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
    result = response.json()

    if result.get('OCRExitCode') != 1 or not result.get('ParsedResults'):
        return jsonify({'error': result.get('ErrorMessage', 'OCR 解析失敗')}), 500

    text = result['ParsedResults'][0].get('ParsedText', '')
    return jsonify({'text': text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
