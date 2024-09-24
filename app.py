from flask import Flask, request, jsonify, send_from_directory, render_template
import cv2
import os
from ultralytics import YOLO
import numpy as np
import base64

app = Flask(__name__)
model = YOLO(r'F:\yolov8s.pt')

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




@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    video_path = os.path.join('uploads', video_file.filename)
    video_file.save(video_path)

    cap = cv2.VideoCapture(video_path)
    last_person_frame_path = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)  # 使用YOLO模型进行检测

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

    cap.release()

    if last_person_frame_path and os.path.exists(last_person_frame_path):
        with open(last_person_frame_path, 'rb') as f:
            last_person_b64 = base64.b64encode(f.read()).decode('utf-8')
    else:
        print("No frame saved; last_person_frame_path is None.")
        last_person_b64 = ''

    print(results)

    return jsonify({'last_person_frame': last_person_b64})

if __name__ == '__main__':
    app.run(debug=True)
