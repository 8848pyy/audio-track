from flask import Flask, request, jsonify, send_from_directory, render_template
import cv2
import os
from ultralytics import YOLO
import numpy as np
import base64

app = Flask(__name__)
model = YOLO(r'F:\yolov8s.pt')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 53秒的视频分析处理耗时05.08秒

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_analysis')
def video_analysis():
    return render_template('video_analysis.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/denglu')
def denglu():
    return render_template('denglu.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/delete_files', methods=['POST'])
def delete_files():
    try:
        if os.path.exists(os.path.join('uploads', 'last_person_frame.jpg')):
            os.remove(os.path.join('uploads', 'last_person_frame.jpg'))
        else:
            print("last_person_frame.jpg does not exist.")

        filename = request.json.get('filename')
        if filename and os.path.exists(os.path.join('uploads', filename)):
            os.remove(os.path.join('uploads', filename))
        else:
            print(f"{filename} does not exist.")

        return jsonify({'message': 'Files deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    video_path = os.path.join('uploads', video_file.filename)
    video_file.save(video_path)

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0
    last_person_frame_path = None
    face_images = []   # 用于保存人脸图像

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)  # 使用YOLO模型进行检测

        # 检测人脸
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

        # 处理检测结果
        if isinstance(results, list):  # 如果results是列表
            for result in results:
                if hasattr(result, 'boxes') and len(result.boxes) > 0:
                    for box in result.boxes:
                        label = int(box.cls)
                        if label == 0:  # 检测到人物
                            last_person_frame_path = os.path.join('uploads', 'last_person_frame.jpg')
                            cv2.imwrite(last_person_frame_path, frame)
                            print(f"Detected person, saved frame to {last_person_frame_path}")
                            break  # 找到一个后可以退出内层循环

        # 保存人脸图像
        for (x, y, w, h) in faces:
            face_image = frame[y:y + h, x:x + w]
            face_image_resized = cv2.resize(face_image, (100, 100))  # 统一大小
            face_filename = f'uploads/face_{processed_frames}_{len(face_images)}.jpg'
            cv2.imwrite(face_filename, face_image_resized)
            face_images.append(face_filename)
            if len(face_images) >= 6:  # 只保存最多6张人脸图像
                break

        processed_frames += 1
        # 这里是关键：计算并返回当前进度
        progress = (processed_frames / total_frames) * 100
        print(f"Processing... {progress:.2f}% complete")

    cap.release()

    if last_person_frame_path and os.path.exists(last_person_frame_path):
        with open(last_person_frame_path, 'rb') as f:

            last_person_b64 = base64.b64encode(f.read()).decode('utf-8')
    else:
        print("No frame saved; last_person_frame_path is None.")
        last_person_b64 = ''

    print(results)

    return jsonify({
        'last_person_frame': last_person_b64,
        'progress': 100,  # 最终进度为100%
        'faces': face_images  # 返回所有人脸图像
    })


if __name__ == '__main__':
    app.run(debug=True)
