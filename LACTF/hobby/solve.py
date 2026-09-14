import matplotlib.pyplot as plt
from data import points 

coords = []

def parse_points():
    data = points.split(", ")
    for tup in data:
        x, y = tup.split(",")
        if "7'd" in x:
            x = int(x[3:]) % 128    
        if "7'd" in y:
            y = int(y[3:]) % 128
        x = int(x)
        y = int(y)

        if x < 128 and y < 128:
            coords.append((x, y))

parse_points()
print(coords)

x_coords, y_coords = zip(*coords)

plt.figure(figsize=(8, 8))
plt.scatter(x_coords, y_coords, s=5, color='blue')

plt.xlim(0, 128)
plt.ylim(128, 0)

plt.title("sol")
plt.xlabel("X (0-127)")
plt.ylabel("Y (0-127)")
plt.grid(True, linestyle='--', alpha=0.5)

plt.show()