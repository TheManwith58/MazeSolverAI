# app.py
import streamlit as st
import cv2
import numpy as np
import os
from collections import deque
from PIL import Image

# Set page config
st.set_page_config(page_title="Maze Solver", page_icon="🧩", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
    }
    .header {
        background: linear-gradient(to right, #7d5a50, #b4846c);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background: linear-gradient(to right, #e17055, #e67e22) !important;
        color: white !important;
        font-weight: bold;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(230, 126, 34, 0.4);
    }
    .result-box {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-top: 1.5rem;
    }
    .image-container {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    .image-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        flex: 1;
        min-width: 300px;
    }
</style>
""", unsafe_allow_html=True)

def find_entry_exit_points(binary_image):
    """Find start and end points on the maze borders"""
    rows, cols = binary_image.shape
    is_path = lambda val: val >= 250  # near-white is considered path
    points = []

    # Scan borders for entry/exit points
    borders = [
        (0, range(cols)),           # Top row
        (rows-1, range(cols)),      # Bottom row
        (range(rows), 0),           # Left column
        (range(rows), cols-1)       # Right column
    ]
    
    for border in borders:
        if isinstance(border[0], int):  # Row scan
            r = border[0]
            for c in border[1]:
                if is_path(binary_image[r, c]):
                    points.append((r, c))
                    break
        else:  # Column scan
            c = border[1]
            for r in border[0]:
                if is_path(binary_image[r, c]):
                    points.append((r, c))
                    break
    
    if len(points) < 2:
        raise Exception("❌ Could not detect two entry/exit points on the maze border.")
    
    return points[0], points[1]

def image_to_grid(img):
    """Convert maze image to binary grid (1=path, 0=wall)"""
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return np.where(binary >= 250, 1, 0)

def bfs(grid, start, end):
    """Breadth-first search pathfinding"""
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
    """Rebuild path from BFS predecessor dictionary"""
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

def draw_path(img, path, color=(0, 0, 255), thickness=2):
    """Draw solution path on the image"""
    # Mark start and end points
    cv2.circle(img, (path[0][1], path[0][0]), 8, (0, 255, 0), -1)  # Green start
    cv2.circle(img, (path[-1][1], path[-1][0]), 8, (0, 0, 255), -1)  # Red end
    
    # Draw path
    for i in range(1, len(path)):
        r1, c1 = path[i-1]
        r2, c2 = path[i]
        cv2.line(img, (c1, r1), (c2, r2), color, thickness)
    
    return img

def solve_maze(image):
    """Complete maze solving workflow: mark points, solve, and visualize"""
    # Convert to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Create binary image for point detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Detect entry/exit points
    try:
        start, end = find_entry_exit_points(binary)
        st.success(f"🟢 Start point detected: ({start[1]}, {start[0]})")
        st.success(f"🔴 End point detected: ({end[1]}, {end[0]})")
    except Exception as e:
        st.error(str(e))
        return None, None, None
    
    # Draw points on original image
    marked_img = img.copy()
    cv2.circle(marked_img, (start[1], start[0]), 8, (0, 255, 0), -1)
    cv2.circle(marked_img, (end[1], end[0]), 8, (0, 0, 255), -1)
    
    # Convert to grid
    grid = image_to_grid(img)
    
    # Solve maze
    prev = bfs(grid, start, end)
    path = reconstruct_path(prev, start, end)
    
    if not path:
        st.error("❌ No path could be found through the maze.")
        return marked_img, None, None
    
    # Draw solution
    solved_img = draw_path(img.copy(), path)
    
    return marked_img, solved_img, path

# UI Components
def main():
    # Header
    st.markdown('<div class="header"><h1>🧩 Maze Solver</h1><p>Upload a maze image to automatically detect entry/exit points and find the solution path</p></div>', 
                unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a maze image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Maze", use_column_width=True)
        
        # Solve button
        if st.button("Solve Maze", use_container_width=True):
            with st.spinner("Solving maze..."):
                # Process image
                marked_img, solved_img, path = solve_maze(image)
                
                if marked_img is not None:
                    # Convert OpenCV images to RGB for display
                    marked_img_rgb = cv2.cvtColor(marked_img, cv2.COLOR_BGR2RGB)
                    marked_img_pil = Image.fromarray(marked_img_rgb)
                    
                    # Display results
                    st.subheader("Results")
                    
                    # Create image columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.image(marked_img_pil, caption="Marked Entry/Exit Points", use_column_width=True)
                    
                    if solved_img is not None:
                        solved_img_rgb = cv2.cvtColor(solved_img, cv2.COLOR_BGR2RGB)
                        solved_img_pil = Image.fromarray(solved_img_rgb)
                        
                        with col2:
                            st.image(solved_img_pil, caption="Solved Maze", use_column_width=True)
                        
                        # Path details
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.subheader("Solution Details")
                        st.success(f"✅ Path found with **{len(path)}** steps")
                        
                        # Download buttons
                        col_d1, col_d2 = st.columns(2)
                        
                        with col_d1:
                            # Save solved image
                            solved_bytes = cv2.imencode('.png', solved_img)[1].tobytes()
                            st.download_button(
                                label="Download Solved Image",
                                data=solved_bytes,
                                file_name="solved_maze.png",
                                mime="image/png"
                            )
                        
                        with col_d2:
                            # Save path coordinates
                            path_text = "\n".join([f"{p[0]} {p[1]}" for p in path])
                            st.download_button(
                                label="Download Path Coordinates",
                                data=path_text,
                                file_name="maze_path.txt",
                                mime="text/plain"
                            )
                        
                        # Path preview
                        with st.expander("View Path Coordinates"):
                            st.code(path_text)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("Failed to process the maze image")

    else:
        # Show sample maze
        st.info("👆 Upload a maze image to get started")
        st.image("https://i.imgur.com/6QqQZ9L.png", caption="Sample Maze", width=400)

# Information sidebar
st.sidebar.title("About Maze Solver")
st.sidebar.markdown("""
This application automatically solves mazes by:

1. Detecting entry and exit points
2. Converting the maze to a grid
3. Finding the shortest path using BFS algorithm
4. Visualizing the solution

### How to use:
1. Upload a maze image (PNG or JPG)
2. Click the "Solve Maze" button
3. View the solution path and download results

### Requirements:
- Maze walls should be dark
- Paths should be light/white
- Entry/exit points should be on the borders
""")

if __name__ == "__main__":
    main()
