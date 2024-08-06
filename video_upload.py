import os
import shutil

UPLOAD_DIR = 'uploads'

def upload_video():
    print("Please enter the path to your video file:")
    video_path = input("Video Path: ")
    allowed_extensions = ['.mp4', '.avi', '.mov']  # Add other video formats if needed
    if os.path.isfile(video_path):
        filename = os.path.basename(video_path)
        extension = os.path.splitext(filename)[1].lower()
        if extension not in allowed_extensions:
            print("Invalid file type. Please upload a video file.")
            return None
        
        new_path = os.path.join(UPLOAD_DIR, filename)
        shutil.copy(video_path, new_path)
        return filename
    else:
        print("File not found. Please check the path and try again.")
        return None
