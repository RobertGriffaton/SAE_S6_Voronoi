import json
import random


def generate_random_points(num_points, x, y):
    points = []
    for point in range(num_points):
        points.append((random.randint(0, x), random.randint(0, y)))
    return points

def main():
    num_points = 45
    x = 100
    y = 150
    points = generate_random_points(num_points, x, y)
    with open("points.json", "w") as f:
        json.dump(points, f)

if __name__ == "__main__":
    main()  
