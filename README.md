# 🎮 Real-Time Gesture Recognition for Interactive Gaming

A computer vision–based interactive gaming system that allows players to control gameplay using **hand gestures in real time** through a standard webcam — eliminating the need for physical controllers.

This project uses **OpenCV**, **MediaPipe**, and **Pygame** to deliver an immersive, touch-free gaming experience.

---

## 🚀 Features

- ✅ Real-time hand detection using webcam  
- ✅ Accurate gesture recognition using MediaPipe  
- ✅ Gesture-based player movement and shooting  
- ✅ Enemy spawning, collision detection, and scoring system  
- ✅ Power-ups and interactive gameplay mechanics  
- ✅ Low-cost solution using only a standard webcam  

---

## 🛠️ Technologies & Libraries Used

| Category | Tools |
|----------|--------|
| Programming Language | Python |
| Computer Vision | OpenCV, MediaPipe |
| Game Development | Pygame |
| Numerical Computing | NumPy |
| IDE | Visual Studio Code / PyCharm |

---

## 🧠 System Architecture

1. Webcam captures live video feed  
2. OpenCV processes each video frame  
3. MediaPipe detects hand landmarks  
4. Gesture recognition logic identifies user actions  
5. Pygame maps gestures to in-game controls  
6. Game engine updates player actions in real time  

---

## 📂 Project Structure

(*File names may vary based on your implementation*)

---

## ⚙️ Installation & Setup

**✅ 1. Clone the Repository**

-> git clone https://github.com/keyan794/Real-Time-Gesture-Recognition-for-Interactive-Gaming

**✅ 2. Create Virtual Environment: **
-> python -m venv venv

Activate it:

Windows: 
-> venv\Scripts\activate
Mac/Linux: 
-> source venv/bin/activate

**✅ 3. Install Dependencies**
-> pip install -r requirements.txt
Or manually:
-> pip install opencv-python mediapipe pygame numpy

**✅ 4. Run the Game**
python main.py

🎯 Game Controls (Gesture-Based)
Hand Gesture	Game Action
Hand Movement	Cursor moves across the screen in real time
Index + Middle Finger Joined	Start shooting
Fingers Separated	Stop shooting
Hand Position	Aims the weapon direction
