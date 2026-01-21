#!/usr/bin/env python3
"""
Download Face Detection and Recognition Models
This script downloads YuNet and SFace models from OpenCV Zoo
"""

import os
import urllib.request
import sys

# Model URLs from OpenCV Zoo
MODELS = {
    'face_detection_yunet_2023mar.onnx': {
        'url': 'https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx',
        'description': 'YuNet Face Detection Model'
    },
    'face_recognition_sface_2021dec.onnx': {
        'url': 'https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx',
        'description': 'SFace Face Recognition Model (lightweight alternative to GhostFaceNet)'
    }
}

def download_file(url, destination):
    """Download file with progress indicator"""
    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r  Progress: {percent}%")
        sys.stdout.flush()

    try:
        print(f"\n  Downloading from: {url}")
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n  ✓ Download complete")
        return True
    except Exception as e:
        print(f"\n  ✗ Download failed: {e}")
        return False

def main():
    """Main function to download all models"""
    print("=" * 70)
    print("Face Recognition Models Downloader")
    print("=" * 70)

    # Create models directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, 'models')

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"\n✓ Created models directory: {models_dir}")
    else:
        print(f"\n✓ Models directory exists: {models_dir}")

    # Download each model
    for filename, info in MODELS.items():
        destination = os.path.join(models_dir, filename)

        print(f"\n{info['description']}")
        print(f"  Target: {destination}")

        if os.path.exists(destination):
            print(f"  ⚠ File already exists, skipping...")
            continue

        success = download_file(info['url'], destination)

        if success:
            file_size = os.path.getsize(destination) / (1024 * 1024)
            print(f"  ✓ File size: {file_size:.2f} MB")
        else:
            print(f"  ✗ Failed to download {filename}")

    print("\n" + "=" * 70)
    print("Download Summary")
    print("=" * 70)

    all_downloaded = True
    for filename in MODELS.keys():
        destination = os.path.join(models_dir, filename)
        if os.path.exists(destination):
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} - MISSING")
            all_downloaded = False

    if all_downloaded:
        print("\n✓ All models downloaded successfully!")
        print("You can now run the facial recognition controller.")
    else:
        print("\n⚠ Some models are missing. Please check the errors above.")
        print("You may need to download them manually from:")
        print("https://github.com/opencv/opencv_zoo")

    print("=" * 70)

if __name__ == '__main__':
    main()
