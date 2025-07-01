# gui.py
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QFileDialog, QVBoxLayout, QWidget, QSpinBox, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QImage
from solver import image_to_grid, bfs, reconstruct_path, draw_path

class MazeSolverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maze Solver")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Image display
        self.image_label = QLabel()
        layout.addWidget(self.image_label)
        
        # Upload button
        self.upload_btn = QPushButton("Upload Maze Image")
        self.upload_btn.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_btn)
        
        # Point selection
        point_layout = QHBoxLayout()
        
        self.start_x_spin = QSpinBox()
        self.start_x_spin.setRange(0, 1000)
        self.start_y_spin = QSpinBox()
        self.start_y_spin.setRange(0, 1000)
        
        self.end_x_spin = QSpinBox()
        self.end_x_spin.setRange(0, 1000)
        self.end_y_spin = QSpinBox()
        self.end_y_spin.setRange(0, 1000)
        
        point_layout.addWidget(QLabel("Start X:"))
        point_layout.addWidget(self.start_x_spin)
        point_layout.addWidget(QLabel("Start Y:"))
        point_layout.addWidget(self.start_y_spin)
        point_layout.addWidget(QLabel("End X:"))
        point_layout.addWidget(self.end_x_spin)
        point_layout.addWidget(QLabel("End Y:"))
        point_layout.addWidget(self.end_y_spin)
        
        layout.addLayout(point_layout)
        
        # Solve button
        self.solve_btn = QPushButton("Solve Maze")
        self.solve_btn.clicked.connect(self.solve_maze)
        self.solve_btn.setEnabled(False)
        layout.addWidget(self.solve_btn)
        
        # Status label
        self.status_label = QLabel("Upload an image to begin")
        layout.addWidget(self.status_label)
        
        self.image = None
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Maze Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is not None:
                # Update spinbox ranges
                height, width, _ = self.image.shape
                self.start_x_spin.setRange(0, width-1)
                self.start_y_spin.setRange(0, height-1)
                self.end_x_spin.setRange(0, width-1)
                self.end_y_spin.setRange(0, height-1)
                
                # Set default start/end
                self.start_x_spin.setValue(0)
                self.start_y_spin.setValue(0)
                self.end_x_spin.setValue(width-1)
                self.end_y_spin.setValue(height-1)
                
                # Display image
                self.display_image(self.image)
                self.solve_btn.setEnabled(True)
                self.status_label.setText("Image loaded. Set points and click Solve")
    
    def display_image(self, image):
        """Display OpenCV image in QLabel"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))
    
    def solve_maze(self):
        if self.image is None:
            return
        
        start = (self.start_y_spin.value(), self.start_x_spin.value())
        end = (self.end_y_spin.value(), self.end_x_spin.value())
        
        # Convert to grid
        grid = image_to_grid(self.image)
        
        # Solve maze
        prev = bfs(grid, start, end)
        path = reconstruct_path(prev, start, end)
        
        if path:
            # Draw solution
            solved_img = draw_path(self.image.copy(), path)
            self.display_image(solved_img)
            self.status_label.setText(f"Path found! Length: {len(path)} steps")
        else:
            self.status_label.setText("No path could be found through the maze")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazeSolverApp()
    window.show()
    sys.exit(app.exec_())