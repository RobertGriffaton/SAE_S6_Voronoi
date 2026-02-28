import json
import random


def generate_random_points(num_points, x, y):
    points = []
    for point in range(num_points):
        points.append((random.randint(-5, x), random.randint(-5, y)))
    return points

def main():
    num_points = 15
    x = 35
    y = 35
    points = generate_random_points(num_points, x, y)
    with open("phase1/points.json", "w") as f:
        json.dump(points, f)

if __name__ == "__main__":
    main()  
