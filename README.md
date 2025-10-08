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

---

## 🛠️ How to Use
1. Load a video file (any common format supported by OpenCV).  
2. Choose an output folder for saving the extracted images.  
3. Click the **Extract Images** button.  
4. CutSnap will automatically process the video and save:  
   - `scene_01_start.jpg`  
   - `scene_01_end.jpg`  
   - `scene_02_start.jpg`  
   - `scene_02_end.jpg`  
   - … and so on.

---

## 📦 Output Example
