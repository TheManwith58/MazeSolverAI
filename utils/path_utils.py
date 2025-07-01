import numpy as np
from collections import deque

def is_valid(x, y, maze, visited):
    h, w = maze.shape
    return 0 <= x < h and 0 <= y < w and maze[x][y] == 255 and not visited[x][y]

def bfs(maze, start, end):
    h, w = maze.shape
    visited = [[False] * w for _ in range(h)]
    parent = {}
    q = deque([start])
    visited[start[0]][start[1]] = True

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # U, D, L, R

    while q:
        x, y = q.popleft()
        if (x, y) == end:
            break
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny, maze, visited):
                visited[nx][ny] = True
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))

    # Reconstruct path
    path = []
    curr = end
    while curr != start:
        path.append(curr)
        curr = parent.get(curr)
        if curr is None:
            return []  # Path not found
    path.append(start)
    path.reverse()
    return path

def draw_path(image, path, color=(0, 0, 255)):
    for x, y in path:
        image[x, y] = color
    return image
