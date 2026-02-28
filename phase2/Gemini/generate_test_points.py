import random

def generate_points(filename="test_points.txt", num_points=30, width=800, height=600):
    """
    Generates a set of random points tailored for the graphical view.
    Points will have a minimum distance from edges.
    """
    margin = 50
    with open(filename, "w", encoding="utf-8") as f:
        for _ in range(num_points):
            x = random.uniform(margin, width - margin)
            y = random.uniform(margin, height - margin)
            f.write(f"{x:.2f},{y:.2f}\n")

if __name__ == "__main__":
    generate_points()
    print("test_points.txt generated successfully!")
