# 🚨 Theft Detection System

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/) 
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green)](https://opencv.org/) 
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)](https://github.com/ultralytics/ultralytics)  
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A **real-time Theft Detection System** using **YOLOv8, Face Recognition, Pose Detection**, and **sound alerts** for restricted areas. Built with **Python** and **OpenCV**, this project detects unauthorized access and sends alerts instantly.

---

## 🔹 Features

- **Real-Time Object Detection** with YOLOv8  
- **Face Recognition** for authorized personnel identification  
- **Pose Detection** for activity monitoring  
- **Sound Alerts** for immediate notification  
- **Telegram Alerts** for remote monitoring  
- **Easy Integration** with multiple cameras and sensors  

---

## 🎬 Demo

![Theft Detection Demo](https://raw.githubusercontent.com/YourUsername/theft-detection/main/assets/demo.gif)
*Animated demo of detection and alert system in action.*

---

## 🛠 Tech Stack

- **Python 3.10+**  
- **OpenCV** – Computer vision tasks  
- **Ultralytics YOLOv8** – Object detection  
- **Face Recognition Library** – Face identification  
- **Sounddevice** – Detect unusual sounds  
- **Telegram Bot API** – Real-time alerts  

---

## ⚡ Installation

1. Clone the repository:
   ```bash



   python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


pip install -r requirements.txt


python main.py

   git clone https://github.com/YourUsername/theft-detection.git
   cd theft-detection

theft-detection/
│
├─ detection/
│   ├─ face_recognize.py
│   └─ pose_detect.py
│
├─ alerts/
│   └─ telegram.py
│
├─ utils/
│   └─ logger.py
│
├─ models/
│   └─ yolov8n.pt
│
└─ main.py
