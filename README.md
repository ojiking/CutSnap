# 🎬 CutSnap
Automatic Video Scene Image Extractor

---

## 🧩 Overview
**CutSnap** is a lightweight tool that automatically detects scene changes in a video and extracts the **first and last frame of each cut** as JPG images.
It’s designed for creators and editors who need fast, organized scene references without handling huge video files.

---

## 🚀 Features
- **Automatic Scene Detection** — Detects scene changes and extracts the first and last frame of each cut.
- **Optimized JPG Output** — Saves images as `.jpg` to reduce file size while maintaining clarity.
- **Smart UI Control** — The “Extract Images” button becomes active only after selecting a video file and output folder.
- **Progress Feedback** — Displays progress updates while processing long videos.

---

## 📦 Installation
1. Ensure you have **Python 3.9+** installed.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Usage
1. Run the application:

   ```bash
   python cutsnap.py
   ```

2. In the UI:
   - Click **“Choose Video”** and select the video file you want to process.
   - Click **“Choose Folder”** and select where the extracted images should be saved.
   - Once both selections are made, the **“Extract Images”** button becomes active.
   - Click the button to start extraction. The app will save images like `scene_01_start.jpg`, `scene_01_end.jpg`, etc., in the chosen folder.

3. When processing finishes you’ll see a confirmation dialog summarizing how many scenes and images were saved.

---

## 🧠 How It Works
CutSnap relies on OpenCV to compare color histograms between consecutive frames. When a significant change is detected, it assumes a new scene has started and saves the first and last frames of the previous scene. The images are written in JPG format to keep file sizes small.

---

## 🛠️ Development Notes
- The scene detection threshold can be tweaked by adjusting the `SceneExtractor`'s `threshold` parameter.
- Image extraction runs in a background thread so the Tkinter UI remains responsive during processing.

---

## 📄 License
MIT License
