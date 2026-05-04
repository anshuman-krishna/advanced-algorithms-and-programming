class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Region:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Region(x={self.x}, y={self.y}, w={self.width}, h={self.height})"

def count_points_in_region(points, rx, ry, rwidth, rheight):
    count = 0
    for pt in points:
        if pt.x >= rx and pt.x <= rx + rwidth and pt.y >= ry and pt.y <= ry + rheight:
            count += 1
    return count

def find_dense_regions(points, x, y, width, height, min_size, density_threshold):
    dense_zones = []
    
    current_count = count_points_in_region(points, x, y, width, height)
    
    if current_count > density_threshold:
        dense_zones.append(Region(x, y, width, height))
        
    if width < min_size or height < min_size:
        return dense_zones
        
    half_w = width / 2.0
    half_h = height / 2.0
    
    top_left = find_dense_regions(points, x, y, half_w, half_h, min_size, density_threshold)
    top_right = find_dense_regions(points, x + half_w, y, half_w, half_h, min_size, density_threshold)
    bottom_left = find_dense_regions(points, x, y + half_h, half_w, half_h, min_size, density_threshold)
    bottom_right = find_dense_regions(points, x + half_w, y + half_h, half_w, half_h, min_size, density_threshold)
    
    dense_zones.extend(top_left)
    dense_zones.extend(top_right)
    dense_zones.extend(bottom_left)
    dense_zones.extend(bottom_right)
    
    return dense_zones

# verification
if __name__ == "__main__":
    print("Initializing Spatial Data:")
    dataset = [
        Point(10, 10), Point(12, 15), Point(15, 12), 
        Point(80, 80), Point(85, 85),
        Point(50, 50) 
    ]
    
    map_size = 100
    min_split_size = 50
    threshold = 2
    
    print(f"Total points generated: {len(dataset)}")
    print(f"Map size: {map_size}x{map_size}, Min split size: {min_split_size}, Density threshold: >{threshold}")
    
    print("\nRunning Spatial Splitting:")
    dense_areas = find_dense_regions(dataset, 0, 0, map_size, map_size, min_split_size, threshold)
    
    print(f"Found {len(dense_areas)} dense regions:")
    for i, region in enumerate(dense_areas):
        points_inside = count_points_in_region(dataset, region.x, region.y, region.width, region.height)
        print(f"[{i+1}] {region} -> contains {points_inside} points")

    print("\nEdge Case Check (The Boundary Bug):")
    midpoint_count = 0
    for r in dense_areas:
        if r.width == 50 and r.height == 50: 
            if count_points_in_region([Point(50, 50)], r.x, r.y, r.width, r.height) > 0:
                midpoint_count += 1
    print(f"A single point at (50, 50) was counted in {midpoint_count} different subregions")