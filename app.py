# app.py
import streamlit as st
import cv2
import numpy as np
from solver import image_to_grid, bfs, reconstruct_path, draw_path
from PIL import Image

st.title("Maze Solver")
st.subheader("Upload a maze image and set start/end points")

# File uploader
uploaded_file = st.file_uploader("Choose a maze image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Process image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Display original image
    st.image(img_rgb, caption="Original Maze", use_column_width=True)
    
    # Point selection
    st.subheader("Set Start and End Points")
    col1, col2 = st.columns(2)
    
    with col1:
        start_x = st.number_input("Start X", min_value=0, max_value=img.shape[1]-1, value=0)
        start_y = st.number_input("Start Y", min_value=0, max_value=img.shape[0]-1, value=0)
    
    with col2:
        end_x = st.number_input("End X", min_value=0, max_value=img.shape[1]-1, value=img.shape[1]-1)
        end_y = st.number_input("End Y", min_value=0, max_value=img.shape[0]-1, value=img.shape[0]-1)
    
    start = (start_y, start_x)
    end = (end_y, end_x)
    
    if st.button("Solve Maze"):
        # Convert to grid
        grid = image_to_grid(img)
        
        # Solve maze
        prev = bfs(grid, start, end)
        path = reconstruct_path(prev, start, end)
        
        if path:
            # Draw solution
            solved_img = draw_path(img, path)
            solved_img_rgb = cv2.cvtColor(solved_img, cv2.COLOR_BGR2RGB)
            
            # Display solution
            st.image(solved_img_rgb, caption="Solved Maze", use_column_width=True)
            st.success(f"Path found! Length: {len(path)} steps")
            
            # Show path coordinates
            with st.expander("Path Coordinates"):
                st.write(path)
        else:
            st.error("No path could be found through the maze")

