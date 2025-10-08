"""CutSnap - Automatic video scene image extractor.

This module provides a small Tkinter-based desktop application that lets a user
select a video file and an output directory. Once both are provided the
"Extract Images" button becomes enabled, and pressing it will extract the first
and last frame of each detected scene cut into JPG images.

Scene detection is achieved with a simple histogram comparison in HSV color
space. The Bhattacharyya distance between consecutive frame histograms is used
as a measure of change, and when the distance exceeds a configurable threshold
(default 0.6) a new scene is assumed.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox


@dataclass
class SceneExtractionResult:
    """Represents the result of a scene extraction run."""

    scenes_detected: int
    frames_extracted: int


class SceneExtractor:
    """Detects scene boundaries and extracts boundary frames from a video."""

    def __init__(self, threshold: float = 0.6) -> None:
        self.threshold = threshold

    def extract(self, video_path: Path, output_dir: Path, progress_callback: Callable[[int], None] | None = None) -> SceneExtractionResult:
        """Extract first and last frames of each scene from ``video_path`` into ``output_dir``.

        Args:
            video_path: Path to the input video file.
            output_dir: Directory where the JPG images will be saved.
            progress_callback: Optional callable receiving the percentage progress (0-100).

        Returns:
            SceneExtractionResult summarizing the run.
        """

        if not video_path.is_file():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise RuntimeError(f"Unable to open video: {video_path}")

        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or None

        success, frame = capture.read()
        if not success or frame is None:
            capture.release()
            raise RuntimeError("Could not read frames from the video.")

        scene_index = 1
        frames_extracted = 0
        scenes_detected = 0

        prev_hist = self._frame_histogram(frame)
        prev_frame = frame.copy()
        current_scene_start = frame.copy()
        frame_index = 1

        while True:
            success, frame = capture.read()
            if not success or frame is None:
                # End of video; save the final scene.
                frames_extracted += self._save_scene_images(output_dir, scene_index, current_scene_start, prev_frame)
                scenes_detected += 1
                break

            hist = self._frame_histogram(frame)
            distance = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)

            if distance > self.threshold:
                frames_extracted += self._save_scene_images(output_dir, scene_index, current_scene_start, prev_frame)
                scenes_detected += 1
                scene_index += 1
                current_scene_start = frame.copy()

            prev_hist = hist
            prev_frame = frame.copy()
            frame_index += 1

            if progress_callback and total_frames:
                progress = int((frame_index / total_frames) * 100)
                progress_callback(min(progress, 100))

        capture.release()

        if progress_callback:
            progress_callback(100)

        return SceneExtractionResult(scenes_detected=scenes_detected, frames_extracted=frames_extracted)

    def _frame_histogram(self, frame: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        return hist

    def _save_scene_images(self, output_dir: Path, scene_index: int, start_frame: np.ndarray, end_frame: np.ndarray) -> int:
        start_path = output_dir / f"scene_{scene_index:02d}_start.jpg"
        end_path = output_dir / f"scene_{scene_index:02d}_end.jpg"

        saved = 0
        if cv2.imwrite(str(start_path), start_frame):
            saved += 1
        if cv2.imwrite(str(end_path), end_frame):
            saved += 1
        return saved


class CutSnapApp(tk.Tk):
    """Tkinter user interface for CutSnap."""

    def __init__(self) -> None:
        super().__init__()
        self.title("CutSnap - Scene Image Extractor")
        self.geometry("520x260")
        self.resizable(False, False)

        self.video_path: Path | None = None
        self.output_dir: Path | None = None
        self.extractor = SceneExtractor()

        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 10}

        tk.Label(self, text="1. Select a video file:").grid(row=0, column=0, sticky="w", **padding)
        self.video_label = tk.Label(self, text="No video selected", fg="gray")
        self.video_label.grid(row=1, column=0, columnspan=2, sticky="w", **padding)
        tk.Button(self, text="Choose Video", command=self.choose_video).grid(row=1, column=2, sticky="e", **padding)

        tk.Label(self, text="2. Select an output folder:").grid(row=2, column=0, sticky="w", **padding)
        self.output_label = tk.Label(self, text="No folder selected", fg="gray")
        self.output_label.grid(row=3, column=0, columnspan=2, sticky="w", **padding)
        tk.Button(self, text="Choose Folder", command=self.choose_output).grid(row=3, column=2, sticky="e", **padding)

        self.progress_var = tk.IntVar(value=0)
        self.progress_label = tk.Label(self, text="Progress: 0%")
        self.progress_label.grid(row=4, column=0, sticky="w", **padding)

        self.extract_button = tk.Button(self, text="Extract Images", state=tk.DISABLED, command=self.extract_images)
        self.extract_button.grid(row=5, column=0, columnspan=3, pady=20)

    def choose_video(self) -> None:
        filetypes = [("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")]
        selection = filedialog.askopenfilename(title="Select video", filetypes=filetypes)
        if selection:
            self.video_path = Path(selection)
            self.video_label.configure(text=str(self.video_path), fg="black")
            self._update_button_state()

    def choose_output(self) -> None:
        selection = filedialog.askdirectory(title="Select output folder")
        if selection:
            self.output_dir = Path(selection)
            self.output_label.configure(text=str(self.output_dir), fg="black")
            self._update_button_state()

    def _update_button_state(self) -> None:
        if self.video_path and self.output_dir:
            self.extract_button.configure(state=tk.NORMAL)
        else:
            self.extract_button.configure(state=tk.DISABLED)

    def extract_images(self) -> None:
        if not self.video_path or not self.output_dir:
            return

        self.extract_button.configure(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.configure(text="Progress: 0%")

        def run_extraction() -> None:
            try:
                result = self.extractor.extract(self.video_path, self.output_dir, progress_callback=self._update_progress)
            except Exception as exc:  # pragma: no cover - user feedback
                self.after(0, lambda: messagebox.showerror("Error", str(exc)))
            else:
                message = (
                    f"Extraction complete!\n"
                    f"Scenes detected: {result.scenes_detected}\n"
                    f"Images saved: {result.frames_extracted}"
                )
                self.after(0, lambda: messagebox.showinfo("Done", message))
            finally:
                self.after(0, self._reset_button)

        threading.Thread(target=run_extraction, daemon=True).start()

    def _update_progress(self, value: int) -> None:
        self.progress_var.set(value)
        self.after(0, lambda: self.progress_label.configure(text=f"Progress: {value}%"))

    def _reset_button(self) -> None:
        if self.video_path and self.output_dir:
            self.extract_button.configure(state=tk.NORMAL)
        else:
            self.extract_button.configure(state=tk.DISABLED)


def main() -> None:
    app = CutSnapApp()
    app.mainloop()


if __name__ == "__main__":
    main()
