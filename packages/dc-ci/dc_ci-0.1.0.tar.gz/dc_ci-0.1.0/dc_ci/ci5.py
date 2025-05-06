text = '''import numpy as np
import random
import matplotlib.pyplot as plt

# Distance matrix between 4 cities
distances = [
    [0, 2, 9, 10],
    [1, 0, 6, 4],
    [15, 7, 0, 8],
    [6, 3, 12, 0]
]

num_cities = len(distances)
num_ants = 5
num_iterations = 50
alpha = 1
beta = 2
evaporation = 0.5

# Random coordinates for cities (for visualization)
np.random.seed(42)
city_coords = np.random.rand(num_cities, 2) * 100

# Initialize pheromone matrix
pheromone = [[1 for _ in range(num_cities)] for _ in range(num_cities)]

# Calculate total distance of a route
def total_distance(route):
    distance = 0
    for i in range(len(route)):
        from_city = route[i]
        to_city = route[(i + 1) % num_cities]
        distance += distances[from_city][to_city]
    return distance

# Select next city based on probability
def choose_next_city(current, visited):
    probs = []
    for j in range(num_cities):
        if j not in visited:
            pher = pheromone[current][j] ** alpha
            heur = (1 / distances[current][j]) ** beta
            probs.append(pher * heur)
        else:
            probs.append(0)
    total = sum(probs)
    probs = [p / total if total > 0 else 0 for p in probs]
    return np.random.choice(range(num_cities), p=probs)

# Main ACO loop
best_route = None
best_cost = float('inf')

for iteration in range(num_iterations):
    all_routes = []
    for ant in range(num_ants):
        start = random.randint(0, num_cities - 1)
        route = [start]
        while len(route) < num_cities:
            next_city = choose_next_city(route[-1], route)
            route.append(next_city)
        all_routes.append(route)

    # Evaporate pheromones
    for i in range(num_cities):
        for j in range(num_cities):
            pheromone[i][j] *= (1 - evaporation)

    # Update pheromones
    for route in all_routes:
        cost = total_distance(route)
        if cost < best_cost:
            best_cost = cost
            best_route = route
        for i in range(num_cities):
            from_city = route[i]
            to_city = route[(i + 1) % num_cities]
            pheromone[from_city][to_city] += 1 / cost

# Print best route and cost
best_route_str = " -> ".join(str(city) for city in best_route + [best_route[0]])
print("Best Route:", best_route_str)
print("Minimum Cost:", best_cost)

# ---------- Visualization ----------
plt.figure(figsize=(6, 6))
for i in range(num_cities):
    x, y = city_coords[i]
    plt.scatter(x, y, c='blue')
    plt.text(x + 1, y + 1, f"City {i}", fontsize=10)

# Draw best path
for i in range(num_cities):
    city_a = best_route[i]
    city_b = best_route[(i + 1) % num_cities]
    x = [city_coords[city_a][0], city_coords[city_b][0]]
    y = [city_coords[city_a][1], city_coords[city_b][1]]
    plt.plot(x, y, 'r-', linewidth=2)

plt.title("Best Route Found by ACO")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.grid(True)
plt.show()
'''

print(text)