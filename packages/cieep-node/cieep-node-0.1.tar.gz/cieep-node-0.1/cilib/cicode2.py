import numpy as np

# Objective function: minimize f(x) = x^2
def objective_function(x):
    return x ** 2

# Initialize population with random values between lower and upper bounds
def initialize_population(size, lower_bound, upper_bound):
    return np.random.uniform(lower_bound, upper_bound, size)

# Clone antibodies (solutions) by repeating them
def clone(antibodies, num_clones):
    return np.repeat(antibodies, num_clones)

# Apply mutation (Gaussian noise) to the clones
def hypermutate(clones, mutation_rate):
    noise = np.random.normal(0, mutation_rate, clones.shape)
    return clones + noise

# Select the best individuals from the population
def select_best(population, num_best):
    fitness = np.array([objective_function(x) for x in population])
    sorted_indices = np.argsort(fitness)  # ascending order (minimization)
    return population[sorted_indices[:num_best]]

# Clonal Selection Algorithm
def clonal_selection_algorithm(pop_size=10, generations=20, clone_factor=5,
                               mutation_rate=0.1, lower_bound=-10, upper_bound=10):
    population = initialize_population(pop_size, lower_bound, upper_bound)
    
    for gen in range(generations):
        fitness = np.array([objective_function(x) for x in population])
        
        # Select best half of the current population
        best = select_best(population, pop_size // 2)
        
        # Clone the best individuals
        clones = clone(best, clone_factor)
        
        # Mutate the clones
        mutated_clones = hypermutate(clones, mutation_rate)
        
        # Clip to bounds
        mutated_clones = np.clip(mutated_clones, lower_bound, upper_bound)
        
        # Select new best individuals from mutated clones
        new_best = select_best(mutated_clones, pop_size)
        
        # Update population with new best clones
        population = new_best
        
        # Print best solution of current generation
        best_solution = population[np.argmin([objective_function(x) for x in population])]
        print(f"Generation {gen+1}: Best Solution = {best_solution:.5f}, Fitness = {objective_function(best_solution):.5f}")
    
    # Final best solution
    return best_solution

# Run the algorithm
best = clonal_selection_algorithm()
print("\nFinal Best Solution:", best)
