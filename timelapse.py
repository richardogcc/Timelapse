import cv2
import os
import argparse
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor

import ttkbootstrap

def create_timelapse(input_folder, output_file, resolution, frame_rate, progress):
    try:
        # Reset the progress bar
        progress['value'] = 0

        # Get all file names in the folder
        filenames = os.listdir(input_folder)

        if not filenames:
            raise ValueError("No images found in the specified folder.")

        # Sort the file names
        filenames.sort()
        # print(filenames)

        # Deduce the video format from the output file extension
        file_extension = os.path.splitext(output_file)[1]
        if file_extension == '.avi':
            video_format = 'XVID'
        elif file_extension == '.mp4':
            video_format = 'mp4v'
        else:
            raise ValueError(f'Unsupported file extension {file_extension}. Please use .avi or .mp4')

        # print(video_format)
        # Define the codec using VideoWriter_fourcc() and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*video_format)
        out = cv2.VideoWriter(output_file, fourcc, frame_rate, resolution)

        if not out.isOpened():
            raise IOError("Error opening video file for writing. Check the output file path and permissions.")

        # Initialize the progress bar
        progress['maximum'] = len(filenames)

        # Process images in batches of 100
        batch_size = 100
        max_workers = 4  # Adjust this value to limit the number of threads

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, len(filenames), batch_size):
                batch_filenames = filenames[i:i+batch_size]
                futures = [executor.submit(cv2.imread, os.path.join(input_folder, filename)) for filename in batch_filenames if filename.endswith(('.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG'))]
                for future in futures:
                    frame = future.result()
                    if frame is None:
                        raise ValueError(f'Error loading image: {batch_filenames[futures.index(future)]}')
                    frame = cv2.resize(frame, resolution)
                    out.write(frame)
                    progress['value'] += 1
                    progress.update()

        # Release the VideoWriter
        out.release()

        # Reset the progress bar
        progress['value'] = 0
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print(f"Error: {e}")

def main():
    try:
        root = tk.Tk()
        root.iconbitmap('main.ico')
        style = ttkbootstrap.Style(theme='darkly')
        root.title('Timelapse Creator')

        input_folder = tk.StringVar()
        output_file = tk.StringVar()
        resolution = tk.StringVar(value="Full HD")
        frame_rate = tk.IntVar(value=25)

        input_folder_button = ttk.Button(root, text="Open Folder", command=lambda: input_folder.set(filedialog.askdirectory()), width=20)
        input_folder_button.pack(pady=(20,10))

        output_file_button = ttk.Button(root, text="Exported File", command=lambda: output_file.set(filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi")])), width=20)
        output_file_button.pack(pady=10)

        resolutions = {"HD": (1280, 720), "Full HD": (1920, 1080), "2K": (2560, 1440), "4K": (3840, 2160)}
        resolution_frame = ttk.Frame(root)
        resolution_frame.pack(pady=10)
        for text, value in resolutions.items():
            ttk.Radiobutton(resolution_frame, text=text, variable=resolution, value=text).pack(side=tk.LEFT, padx=10)

        frame_rates = {"20 FPS": 20, "24 FPS": 24, "25 FPS": 25, "30 FPS": 30, "60 FPS": 60}
        frame_rate_frame = ttk.Frame(root)
        frame_rate_frame.pack(pady=10)
        for text, value in frame_rates.items():
            ttk.Radiobutton(frame_rate_frame, text=text, variable=frame_rate, value=value).pack(side=tk.LEFT, padx=10)

        progress = ttk.Progressbar(root, length=100, mode='determinate')
        progress.pack(pady=10)

        create_button = ttk.Button(root, text="Export", command=lambda: create_timelapse(input_folder.get(), output_file.get(), resolutions[resolution.get()], frame_rate.get(), progress), width=20)
        create_button.pack(pady=(10,20), padx=50)

        root.mainloop()
    except Exception as e:
        messagebox.showerror("Initialization Error", str(e))
        print(f"Initialization Error: {e}")

if __name__ == "__main__":
    main()
