import cv2
import numpy as np
import os
from collections import deque

def load_start_end_points(file_path="points.txt"):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            start = tuple(map(int, lines[0].split()))
            end = tuple(map(int, lines[1].split()))
            return start, end
    except:
        raise Exception(" Could not read start/end from points.txt")

def image_to_grid(img, white_threshold=240):
    """
    Converts a maze image with colored markers to a clean binary grid.
    1 = path (white), 0 = wall (black).
    Removes red and green markers first.
    """
    # Create a copy to modify
    clean_img = img.copy()

    # Mask green (start) and red (end) dots
    lower_red = np.array([0, 0, 100])
    upper_red = np.array([80, 80, 255])

    lower_green = np.array([0, 100, 0])
    upper_green = np.array([80, 255, 80])

    mask_red = cv2.inRange(clean_img, lower_red, upper_red)
    mask_green = cv2.inRange(clean_img, lower_green, upper_green)

    clean_img[mask_red > 0] = [255, 255, 255]   # Replace red with white
    clean_img[mask_green > 0] = [255, 255, 255] # Replace green with white

    # Now convert to grayscale and threshold
    gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
    grid = np.where(gray >= white_threshold, 1, 0)

    return grid

def bfs(grid, start, end):
    rows, cols = grid.shape
    visited = np.zeros_like(grid, dtype=bool)
    prev = {}

    queue = deque([start])
    visited[start] = True

    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            break

        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr, nc] == 1 and not visited[nr, nc]:
                    visited[nr, nc] = True
                    queue.append((nr, nc))
                    prev[(nr, nc)] = (r, c)

    return prev

def reconstruct_path(prev, start, end):
    path = []
    current = end
    while current != start:
        if current not in prev:
            return []
        path.append(current)
        current = prev[current]
    path.append(start)
    path.reverse()
    return path

def draw_path(img, path, color=(255, 0, 0), thickness=1):
    for (r, c) in path:
        cv2.circle(img, (c, r), thickness, color, -1)
    return img

# === Main Execution ===
def solve_maze(input_image_path="maze_marked.png", output_path="solution.png"):
    try:
        img = cv2.imread(input_image_path)
        if img is None:
            print(f"Could not load image from {input_image_path}")
            return False

        start, end = load_start_end_points()
        grid = image_to_grid(img)
        prev = bfs(grid, start, end)
        path = reconstruct_path(prev, start, end)

        if not path:
            print("No path found in the maze.")
            return False

        solved_img = draw_path(img.copy(), path)
        cv2.imwrite(output_path, solved_img)
        return True
    except Exception as e:
        print("Solver error:", e)
        return False
