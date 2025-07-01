import cv2
import numpy as np

def find_border_entry_exit(binary_image):
    rows, cols = binary_image.shape
    white = lambda val: val >= 250
    points = []

    # Top
    for c in range(cols):
        if white(binary_image[0, c]):
            points.append((0, c))
            break

    # Bottom
    for c in range(cols):
        if white(binary_image[rows - 1, c]) and len(points) < 2:
            points.append((rows - 1, c))
            break

    # Left
    for r in range(rows):
        if white(binary_image[r, 0]) and len(points) < 2:
            points.append((r, 0))
            break

    # Right
    for r in range(rows):
        if white(binary_image[r, cols - 1]) and len(points) < 2:
            points.append((r, cols - 1))
            break

    if len(points) < 2:
        raise Exception("Could not detect two entry/exit points on the maze border.")

    return points[0], points[1]

def mark_maze(input_path="maze.png", output_path="maze_marked.png"):
    try:
        # Read grayscale image
        img_gray = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img_gray is None:
            raise Exception("Maze image not found.")

        # Convert to binary
        _, binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

        # Detect start/end points
        start, end = find_border_entry_exit(binary)

        # Read color image for marking
        img_color = cv2.imread(input_path)
        if img_color is None:
            raise Exception("Failed to load color image.")

        # Mark the points
        cv2.circle(img_color, (start[1], start[0]), 5, (0, 255, 0), -1)
        cv2.circle(img_color, (end[1], end[0]), 5, (0, 0, 255), -1)

        # Save marked image
        cv2.imwrite(output_path, img_color)

        # Save coordinates
        with open("points.txt", "w") as f:
            f.write(f"{start[0]} {start[1]}\n")
            f.write(f"{end[0]} {end[1]}\n")

        print(f"✅ Marked maze saved. Start: {start}, End: {end}")
        return True

    except Exception as e:
        print("Marking failed:", e)
        return False
