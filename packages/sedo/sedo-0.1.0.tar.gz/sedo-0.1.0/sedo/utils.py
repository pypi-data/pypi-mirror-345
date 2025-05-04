import matplotlib.pyplot as plt
import pickle
import json
import numpy as np
from typing import List, Dict

def plot_convergence(history: List[Dict[str, float]]) -> None:
    fitnesses = [h['best_fitness'] for h in history]
    plt.plot(fitnesses, label='Best Fitness')
    plt.xlabel("Iteration")
    plt.ylabel("Fitness")
    plt.title("Convergence Curve")
    plt.legend()
    plt.grid(True)
    plt.show()

def save_checkpoint(optimizer, file_path: str) -> None:
    state = {
        'particles': optimizer.particles,
        'global_best_pos': optimizer.global_best_pos,
        'global_best_fit': optimizer.global_best_fit,
        'history': optimizer.history,
        'diversity_history': optimizer.diversity_history,
        'temperature': optimizer.temperature
    }
    with open(file_path, 'wb') as f:
        pickle.dump(state, f)

def load_checkpoint(file_path: str) -> dict:
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def export_results(optimizer, file_path: str, fmt: str = 'json') -> None:
    result = {
        'best_solution': optimizer.get_best_solution().tolist(),
        'best_fitness': optimizer.global_best_fit,
        'history': optimizer.history
    }
    if fmt == 'json':
        with open(file_path, 'w') as f:
            json.dump(result, f, indent=2)
    elif fmt == 'csv':
        import pandas as pd
        df = pd.DataFrame(optimizer.history)
        df.to_csv(file_path, index=False)