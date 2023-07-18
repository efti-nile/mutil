import cv2
import numpy as np
import logging
import os
import shutil
import re


def get_frames(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames


def create_empty_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)


def get_only_filename(file_path):
    base_name = os.path.basename(file_path)  
    filename, extension = os.path.splitext(base_name)  
    return filename


def add_postfix_to_name(file_path, prefix):
    result = re.sub(r'(\.[a-zA-Z0-9]+)$',
                    prefix + r'\1',
                    file_path)
    return result


def color2pixel(color):
    return np.array(color[::-1]).reshape([1, 1, 3])


def get_rgb_delta(image, color):
    image = np.array(image, dtype=np.double)
    pixel = np.array(color2pixel(color), dtype=np.double)
    rgb_delta = np.linalg.norm(image - pixel, axis=2)
    return rgb_delta


def get_mask(image, color, tolerance=20, fill_value=255):
    delta = get_rgb_delta(image, color)
    _, mask_f = cv2.threshold(delta, tolerance, fill_value, cv2.THRESH_BINARY)
    mask_u8 = np.array(mask_f, dtype=np.uint8)
    return fill_value - mask_u8  # inverse the image
  

def count_pixels(image, color):
    delta = get_rgb_delta(image, color)
    delta_flatten = delta.flatten()
    num_matches = (np.abs(delta_flatten) == 0).sum()
    return num_matches


def morph_dilate(image, kernel_size=5, iterations=1):
    kernel = np.ones((kernel_size, kernel_size))
    dilated = cv2.dilate(image, kernel, iterations=iterations)
    return dilated
    


def morph_open(image, kernel_size=5):
    kernel = np.ones((kernel_size, kernel_size),
                     dtype=np.uint8)
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    return opened


def play(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()    
