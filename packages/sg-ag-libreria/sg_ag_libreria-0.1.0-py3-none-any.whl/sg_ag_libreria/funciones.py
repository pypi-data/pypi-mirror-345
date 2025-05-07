import random

def funcion_objetvio(x):
    return x ** 2

def crear_individuo(valor_min,valor_max):
    return random.uniform(valor_min,valor_max)

def torneo(poblacion, fitness):
    i, j = random.sample(range(len(poblacion)), 2)
    return poblacion[i] if fitness[i] < fitness[j] else poblacion[j]

def crossover(p1, p2, rate):
    if random.random() < rate:
        α = random.random()
        return α * p1 + (1 - α) * p2, α * p2 + (1 - α) * p1
    return p1, p2

def mutar(x, mutation_rate, valor_min, valor_max):
    if random.random() < mutation_rate:
        return x + random.gauss(0, (valor_max - valor_min) * 0.1)
    return x

def algoritmo_genetico(pop_size, valor_min, valor_max, generations, crossover_rate, mutation_rate):
    poblacion = [crear_individuo(valor_min, valor_max) for _ in range(pop_size)]
    for _ in range(generations):
        fitness = [funcion_objetvio(ind) for ind in poblacion]
        nueva_pob = []
        while len(nueva_pob) < pop_size:
            padre1 = torneo(poblacion, fitness)
            padre2 = torneo(poblacion, fitness)
            hijo1, hijo2 = crossover(padre1, padre2, crossover_rate)
            nueva_pob.extend([
                mutar(hijo1, mutation_rate, valor_min, valor_max),
                mutar(hijo2, mutation_rate, valor_min, valor_max)
            ])
        poblacion = nueva_pob[:pop_size]
    fitness_final = [funcion_objetvio(ind) for ind in poblacion]
    return poblacion[fitness_final.index(min(fitness_final))]

