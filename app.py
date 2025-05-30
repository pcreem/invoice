from flask import Flask, request, jsonify, send_from_directory
import os
import io
import requests
import cv2
import numpy as np

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')

OCR_SPACE_API_KEY = 'K82170038988957'
MAX_IMAGE_SIZE_KB = 500
FORCE_COMPRESS_IF_OVER_KB = 1024  # 若超過 1MB 強制壓縮
TARGET_COMPRESS_KB = 300          # 壓縮目標：小於 500KB

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def preprocess_image(file_stream, max_size_kb=MAX_IMAGE_SIZE_KB):
    # 讀取原始圖片
    raw_bytes = file_stream.read()
    file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # 如果圖片原始大小 > 1MB，先縮小尺寸 50%
    if len(raw_bytes) > FORCE_COMPRESS_IF_OVER_KB * 1024:
        image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))

    # 預處理：灰階、銳化、二值化
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    _, thresh = cv2.threshold(sharpened, 150, 255, cv2.THRESH_BINARY)

    # 嘗試用不同品質壓縮 JPEG，直到小於 500KB 或 max_size_kb
    target_kb = min(max_size_kb, TARGET_COMPRESS_KB)
    for quality in range(80, 20, -10):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded_image = cv2.imencode('.jpg', thresh, encode_param)
        if not success:
            continue
        if len(encoded_image) <= target_kb * 1024:
            img_io = io.BytesIO(encoded_image.tobytes())
            img_io.seek(0)
            return img_io

    raise ValueError(f'無法將圖片壓縮到 {target_kb}KB 以下')

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
