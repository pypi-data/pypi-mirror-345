text ='''import random
from deap import base, creator, tools

# Step 1: Define the fitness function (we want to minimize)
def eval_func(individual):
    x, y = individual
    return x**2 + y**2,  # Comma means it's a tuple

# Step 2: Define individual and fitness types
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimize
creator.create("Individual", list, fitness=creator.FitnessMin)

# Step 3: Create the toolbox and register components
toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -5.0, 5.0)  # Value range
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=2)  # 2D
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", eval_func)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# Step 4: Run the Genetic Algorithm
population = toolbox.population(n=10)
generations = 10

for gen in range(generations):
    offspring = toolbox.select(population, len(population))
    offspring = list(map(toolbox.clone, offspring))

    # Apply crossover and mutation
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1, child2)
            del child1.fitness.values, child2.fitness.values

    for mutant in offspring:
        if random.random() < 0.2:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Evaluate new individuals
    for ind in offspring:
        if not ind.fitness.valid:
            ind.fitness.values = toolbox.evaluate(ind)

    population[:] = offspring

# Step 5: Show the best solution
best = tools.selBest(population, 1)[0]
print("Best individual:", best)
print("Best fitness:", best.fitness.values[0])'''

print(text)
