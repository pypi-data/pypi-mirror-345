code = '''
import numpy as np

# Objective function to minimize
def objective_function(x):
    return x ** 2

# Clonal Selection Algorithm
def clonal_selection(pop_size=10, generations=20, clone_factor=5, mutation_rate=0.1, lower=-10, upper=10):
    # Step 1: Initialize random population
    population = np.random.uniform(lower, upper, pop_size)

    for gen in range(generations):
        # Step 2: Evaluate fitness
        fitness = objective_function(population)
        
        # Step 3: Select best half
        best_indices = np.argsort(fitness)[:pop_size // 2]
        best = population[best_indices]

        # Step 4: Clone best solutions
        clones = np.repeat(best, clone_factor)

        # Step 5: Apply mutation
        mutations = np.random.normal(0, mutation_rate, size=clones.shape)
        clones = clones + mutations

        # Step 6: Select new best solutions
        new_fitness = objective_function(clones)
        best_new_indices = np.argsort(new_fitness)[:pop_size]
        population = clones[best_new_indices]

        # Report best solution so far
        best_solution = population[np.argmin(objective_function(population))]
        print(f"Generation {gen+1}: Best = {best_solution:.5f}, Fitness = {objective_function(best_solution):.5f}")

    return best_solution

# Run the algorithm
best = clonal_selection()
print("Final Best Solution:", best)
'''

print(code)