import random

def midpoint_displacement(x1, y1, x2, y2, roughness, depth, points):
    if depth == 0:
        return
    midX = (x1 + x2) / 2
    midY = (y1 + y2) / 2
    offset = roughness * random.uniform(-1, 1)
    midY = midY + offset
    points.append((midX, midY))
    midpoint_displacement(x1, y1, midX, midY, roughness, depth - 1, points)
    midpoint_displacement(midX, midY, x2, y2, roughness, depth - 1, points)

def generate_terrain(width, height, roughness, depth):
    terrain = [[0 for _ in range(height)] for _ in range(width)]
    points = []
    midpoint_displacement(0, 0, width - 1, 0, roughness, depth, points)
    for x, y in points:
        xi = int(x)
        yi = int(abs(y)) % height
        terrain[xi][yi] = 1
    return terrain

def detect_artifacts(terrain_grid, threshold):
    suspicious_cells = []
    rows = len(terrain_grid)
    cols = len(terrain_grid[0])
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    for i in range(rows):
        for j in range(cols):
            for dx, dy in directions:
                ni, nj = i + dx, j + dy
                if 0 <= ni < rows and 0 <= nj < cols:
                    if abs(terrain_grid[i][j] - terrain_grid[ni][nj]) > threshold:
                        suspicious_cells.append((i, j))
                        break
    return suspicious_cells