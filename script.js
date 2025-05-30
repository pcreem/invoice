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

document.getElementById('copyButton').addEventListener('click', function () {
    const text = document.getElementById('recognizedText').textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('文字已複製');
    });
});
