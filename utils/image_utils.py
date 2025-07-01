import cv2
import numpy as np

def load_maze(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    return img

def preprocess_maze(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return binary

def find_point_by_color(image, target_color):
    # Finds first pixel matching the target BGR color
    match = np.where(np.all(image == target_color, axis=-1))
    if len(match[0]) == 0:
        return None
    return (match[0][0], match[1][0])
