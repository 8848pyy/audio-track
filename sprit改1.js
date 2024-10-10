document.addEventListener('DOMContentLoaded', function() {
    const videoUpload = document.getElementById('videoUpload');
    const videoPlayer = document.getElementById('videoPlayer');
    const analyzeButton = document.querySelector('.button-style');
    const lastPersonImage = document.getElementById('last_person_frame');
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('progressBar');
    const progress = document.getElementById('progress');

    videoUpload.addEventListener('change', function() {
        const file = videoUpload.files[0];
        if (file) {
            // 删除旧文件
            fetch('/delete_files', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: videoUpload.value.split('\\').pop() })
            }).then(response => {
                if (!response.ok) {
                    console.error('Error deleting files:', response);
                }
            });

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

        // 显示进度条和状态文本
        statusText.textContent = '请稍等片刻，视频正在分析！';
        progressBar.style.display = 'block';
        progress.style.width = '0%'; // 重置进度条

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            console.log(data); // 查看完整返回数据

            // 更新最后一帧的人物图像
            if (data.last_person_frame) {
                lastPersonImage.src = `/uploads/last_person_frame.jpg?t=${new Date().getTime()}`; // 强制刷新
            } else {
                lastPersonImage.src = ''; // 没有检测到人物时清空
            }

            // 显示人脸图像
            const faceImagesContainer = document.getElementById('faceImagesContainer');
            faceImagesContainer.innerHTML = ''; // 清空旧的图像
            data.faces.forEach(face => {
                const img = document.createElement('img');
                img.src = face; // 设置图像路径
                img.alt = '人脸图像';
                img.style.width = '100px'; // 设置宽度
                img.style.height = 'auto'; // 自适应高度
                img.style.marginRight = '10px'; // 设置间距
                faceImagesContainer.appendChild(img);
            });

            // 假设数据中返回了处理进度
            if (data.progress === 100) {
                statusText.textContent = '视频已分析完成，以下是最后出现在视频中的人物图片';
            }

            // 模拟进度条加载完成
            let width = 0;
            const interval = setInterval(() => {
                if (width >= 100) {
                    clearInterval(interval);
                    progressBar.style.display = 'none'; // 隐藏进度条
                } else {
                    width++;
                    progress.style.width = width + '%';
                }
            }, 10); // 每30毫秒增加1%
        })
        .catch(error => {
            console.error('Error:', error);
            progressBar.style.display = 'none'; // 隐藏进度条
        });
    });
});
