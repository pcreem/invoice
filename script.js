document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const progressBar = document.getElementById('progressBar');
    const resultDiv = document.getElementById('result');
    const recognizedText = document.getElementById('recognizedText');

    progressBar.style.display = 'block';
    resultDiv.style.display = 'none';
    recognizedText.textContent = '';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        progressBar.style.display = 'none';
        resultDiv.style.display = 'block';

        if (data.text) {
            recognizedText.textContent = data.text;
        } else {
            recognizedText.textContent = `錯誤: ${data.error}`;
        }
    })
    .catch(error => {
        progressBar.style.display = 'none';
        recognizedText.textContent = `錯誤: ${error}`;
        resultDiv.style.display = 'block';
        console.error('錯誤:', error);
    });
});

document.getElementById('fileInput').addEventListener('change', function() {
    const file = this.files[0];
    const preview = document.getElementById('imagePreview');
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        preview.src = '';
        preview.style.display = 'none';
    }
});

document.getElementById('copyButton').addEventListener('click', function () {
    const text = document.getElementById('recognizedText').textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('文字已複製');
    });
});

function downloadBlob(content, mimeType, filename) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

document.getElementById('downloadTxt').addEventListener('click', function () {
    const text = document.getElementById('recognizedText').textContent;
    downloadBlob(text, 'text/plain', 'recognized.txt');
});

document.getElementById('downloadDoc').addEventListener('click', function () {
    const text = document.getElementById('recognizedText').textContent;
    downloadBlob(text, 'application/msword', 'recognized.doc');
});

document.getElementById('downloadDocx').addEventListener('click', function () {
    const text = document.getElementById('recognizedText').textContent;
    downloadBlob(text, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'recognized.docx');
});
