document.addEventListener('DOMContentLoaded', function() {
    const videoUpload = document.getElementById('videoUpload');
    const videoPlayer = document.getElementById('videoPlayer');
    const analyzeButton = document.querySelector('.button-style');
    const lastPersonImage = document.getElementById('last_person_frame'); // 确保使用正确的 ID

    videoUpload.addEventListener('change', function() {
        const file = videoUpload.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            videoPlayer.src = url;
            videoPlayer.play();
        }
    });

    analyzeButton.addEventListener('click', function() {
        const videoFile = videoUpload.files[0];
        if (!videoFile) {
            alert('请先选择一个视频文件');
            return;
        }

        const formData = new FormData();
        formData.append('video', videoFile);

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const analysisResultDiv = document.getElementById('analysisResult');
            analysisResultDiv.innerHTML = ''; // 清空结果区域

            const title = document.createElement('h3');
            title.textContent = '最后一帧检测到的人物：';
            analysisResultDiv.appendChild(title);

            // 更新最后一帧的人物图像
            if (data.last_person_frame) {
                lastPersonImage.src = `data:image/jpeg;base64,${data.last_person_frame}`; // 使用 Base64 更新人物图像
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
