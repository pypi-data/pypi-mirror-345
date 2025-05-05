# sedo/search.py

from typing import Callable, Dict, List, Optional, Union, Any
import numpy as np
from .optimizer import SEDOptimizer
from .utils import plot_convergence

# 全局可访问的目标函数（用于多进程）
def _search_objective(estimator, keys, x):
    params = {k: val for k, val in zip(keys, x)}
    scores = []
    for _ in range(3):  # 默认 cv=3
        score = estimator(x)
        scores.append(score)
    return np.mean(scores)

class SEDSearchCV:
    def __init__(
        self,
        estimator: Callable[[np.ndarray], float],
        param_space: Dict[str, List[float]],
        n_particles: int = 30,
        max_iter: int = 100,
        scoring: Optional[Callable] = None,
        cv: int = 3,
        verbose: int = 1
    ):
        self.estimator = estimator
        self.param_space = param_space
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.scoring = scoring or (lambda x: -x)
        self.cv = cv
        self.verbose = verbose
        self.best_params_ = None
        self.best_score_ = float('inf')

    def fit(self, X=None, y=None):
        keys = list(self.param_space.keys())
        bounds = [(min(v), max(v)) for v in self.param_space.values()]
        problem_dim = len(keys)

        # 使用闭包或 partial 构造一个可序列化的目标函数
        from functools import partial
        objective_func = partial(_search_objective, self.estimator, keys)

        opt = SEDOptimizer(
            objective_func=objective_func,
            problem_dim=problem_dim,
            n_particles=self.n_particles,
            bounds=bounds,
        )
        opt.optimize(self.max_iter)
        best_x = opt.get_best_solution()
        self.best_params_ = {k: v for k, v in zip(keys, best_x)}
        self.best_score_ = opt.global_best_fit
        self.optimizer_ = opt

    def plot_convergence(self):
        plot_convergence(self.optimizer_.history)