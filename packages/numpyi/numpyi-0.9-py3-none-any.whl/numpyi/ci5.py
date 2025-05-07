code = '''
import numpy as np

# Distance matrix between cities (symmetric)
cities = np.array([
    [0, 2, 9, 10, 7, 14, 11],
    [1, 0, 6, 4, 12, 8, 10],
    [15, 7, 0, 8, 6, 9, 13],
    [6, 3, 12, 0, 9, 11, 5],
    [7, 12, 6, 9, 0, 4, 8],
    [14, 8, 9, 11, 4, 0, 6],
    [11, 10, 13, 5, 8, 6, 0]
])

# ACO parameters
num_ants = 10
num_iterations = 100
decay = 0.1
alpha = 1   # Pheromone importance
beta = 2    # Distance importance

num_cities = cities.shape[0]
pheromone = np.ones((num_cities, num_cities)) / num_cities

best_cost = float('inf')
best_path = None

# Calculate route distance
def route_distance(route):
    dist = 0
    for i in range(len(route)):
        dist += cities[route[i - 1], route[i]]
    return dist

# Choose next city based on probabilities
def select_next_city(probabilities):
    return np.random.choice(range(len(probabilities)), p=probabilities)

# Main ACO loop
for iteration in range(num_iterations):
    all_routes = []
    all_distances = []

    for ant in range(num_ants):
        visited = []
        current_city = np.random.randint(num_cities)
        visited.append(current_city)

        while len(visited) < num_cities:
            unvisited = list(set(range(num_cities)) - set(visited))
            pheromone_values = np.array([pheromone[current_city][j] for j in unvisited])
            distances = np.array([cities[current_city][j] for j in unvisited])
            heuristic = 1 / distances
            prob = (pheromone_values ** alpha) * (heuristic ** beta)
            prob /= prob.sum()
            next_city = unvisited[select_next_city(prob)]
            visited.append(next_city)
            current_city = next_city

        route = visited
        distance = route_distance(route)
        all_routes.append(route)
        all_distances.append(distance)

        if distance < best_cost:
            best_cost = distance
            best_path = route

    # Evaporate pheromone
    pheromone *= (1 - decay)

    # Deposit new pheromones
    for route, dist in zip(all_routes, all_distances):
        for i in range(num_cities):
            a, b = route[i - 1], route[i]
            pheromone[a][b] += 1 / dist

# Output best solution
print("Best path:", best_path + [best_path[0]])  # To complete the cycle
print("Best cost:", best_cost)

'''

print(code)