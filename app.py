from flask import Flask, request, jsonify, send_from_directory
import os
import io
import requests
import cv2
import numpy as np

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')

OCR_SPACE_API_KEY = 'K82170038988957'  # 替換為你的 OCR.Space 金鑰
MAX_IMAGE_SIZE_KB = 900  # 壓縮限制

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def preprocess_image(file_stream, max_size_kb=MAX_IMAGE_SIZE_KB):
    # 將圖片讀取為 OpenCV 格式
    file_bytes = np.asarray(bytearray(file_stream.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # 圖像預處理（灰階 + 銳化 + 二值化）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    _, thresh = cv2.threshold(sharpened, 150, 255, cv2.THRESH_BINARY)

    # 嘗試以不同壓縮品質輸出 JPEG，直到檔案小於 max_size_kb
    for quality in range(80, 30, -10):  # 可微調範圍
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded_image = cv2.imencode('.jpg', thresh, encode_param)
        if not success:
            continue
        if len(encoded_image) <= max_size_kb * 1024:
            img_io = io.BytesIO(encoded_image.tobytes())
            img_io.seek(0)
            return img_io

    raise ValueError(f'無法將圖片壓縮到 {max_size_kb}KB 以下')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '未找到檔案'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未選擇檔案'}), 400

    try:
        processed_image = preprocess_image(file.stream)

        payload = {
            'apikey': OCR_SPACE_API_KEY,
            'language': 'cht',
            'isOverlayRequired': False,
            'filetype': 'JPG'
        }

        files = {
            'file': ('processed.jpg', processed_image, 'image/jpeg')
        }

        response = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
        result = response.json()

        if result.get('OCRExitCode') != 1 or not result.get('ParsedResults'):
            return jsonify({'error': result.get('ErrorMessage', 'OCR 解析失敗')}), 500

        text = result['ParsedResults'][0].get('ParsedText', '')
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'處理或辨識失敗：{str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
