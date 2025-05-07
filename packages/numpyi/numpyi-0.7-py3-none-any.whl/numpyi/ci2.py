code = '''
import numpy as np

def objective_function(x):
    return x ** 2

def initialize_population(size, lower_bound, upper_bound):
    return np.random.uniform(lower_bound, upper_bound, size)

def clone(antibodies, num_clones):
    return np.repeat(antibodies, num_clones)

def hypermutate(clones, mutation_rate):
    noise = np.random.normal(0, mutation_rate, clones.shape)
    return clones + noise

def select_best(population, num_best):
    fitness = np.array([objective_function(x) for x in population])
    sorted_indices = np.argsort(fitness)
    return population[sorted_indices[:num_best]]

def clonal_selection_algorithm(pop_size=10, generations=20, clone_factor=5, mutation_rate=0.1,
                               lower_bound=-10, upper_bound=10):
    population = initialize_population(pop_size, lower_bound, upper_bound)

    for gen in range(generations):
        fitness = np.array([objective_function(x) for x in population])
        best = select_best(population, pop_size // 2)
        clones = clone(best, clone_factor)
        mutated_clones = hypermutate(clones, mutation_rate)
        new_best = select_best(mutated_clones, pop_size)
        population = new_best
        best_solution = population[np.argmin([objective_function(x) for x in population])]
        print(f"Generation {gen+1}: Best Solution = {best_solution:.5f}, Fitness = {objective_function(best_solution):.5f}")

    return best_solution

best = clonal_selection_algorithm()
print("\nFinal Best Solution:", best)


'''

print(code)