import matplotlib.pyplot as plt
import pickle
import json
import numpy as np
from typing import List, Dict, Optional, Tuple

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

def plot_pareto_front(pareto_front: List[List[float]], 
                      obj_names: Optional[List[str]] = None,
                      title: str = "Pareto Front",
                      show_grid: bool = True,
                      figsize: Tuple[int, int] = (8, 6)) -> None:
    """
    可视化多目标优化中的 Pareto 前沿解集
    
    参数:
        pareto_front: List[List[float]] - 非支配解的目标函数值列表
        obj_names: Optional[List[str]] - 目标名称（如 ['Weight', 'Stress']）
        title: 图形标题
        show_grid: 是否显示网格
        figsize: 图像大小
    """
    pareto_array = np.array(pareto_front)

    plt.figure(figsize=figsize)
    plt.scatter(pareto_array[:, 0], pareto_array[:, 1], c='blue', label='Pareto Front')

    if obj_names and len(obj_names) >= 2:
        plt.xlabel(obj_names[0])
        plt.ylabel(obj_names[1])
    else:
        plt.xlabel('Objective 1')
        plt.ylabel('Objective 2')

    plt.title(title)
    plt.grid(show_grid)
    plt.legend()
    plt.tight_layout()
    plt.show()
