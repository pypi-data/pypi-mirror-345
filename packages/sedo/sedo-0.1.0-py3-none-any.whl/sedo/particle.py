import numpy as np
import random
from typing import List, Tuple, Optional

class ExplorationState:
    """表示粒子处于探索状态"""
    pass

class ExploitationState:
    """表示粒子处于开发状态"""
    pass

class QuantumParticle:
    """
    表示一个量子态粒子，具有文化维度、熵值、位置等属性
    """

    def __init__(self, problem_dim: int, discrete_dims: Optional[List[int]] = None):
        self.discrete_dims: List[int] = discrete_dims or []
        self.cultural_dimension: np.ndarray = np.random.normal(0, 1, 6)
        self.entropy_phase: complex = complex(random.random(), random.random())
        self.positive_entropy: float = random.random()
        self.negative_entropy: float = random.random()
        self.superposition = [ExplorationState(), ExploitationState()]
        self.position: Optional[np.ndarray] = None
        self.velocity: Optional[np.ndarray] = None
        self.fitness: float = float('inf')
        self.collapsed: bool = False
        self.state: Optional[Any] = None

    def set_position(self, position: np.ndarray, bounds: List[Tuple[float, float]]) -> None:
        pos = np.array(position)
        for i in range(len(pos)):
            if i in self.discrete_dims:
                pos[i] = round(pos[i])
            pos[i] = np.clip(pos[i], bounds[i][0], bounds[i][1])
        self.position = pos

    def init_random_position(self, bounds: List[Tuple[float, float]], method: str = 'uniform') -> None:
        if method == 'lhs':
            self.position = np.array([np.random.uniform(b[0], b[1]) for b in bounds])
        elif method == 'orthogonal':
            self.position = np.array([(b[0] + b[1]) / 2 + np.random.uniform(-0.5, 0.5) for b in bounds])
        else:
            self.position = np.array([np.random.uniform(b[0], b[1]) for b in bounds])

        for i in self.discrete_dims:
            self.position[i] = round(self.position[i])

        self.velocity = np.zeros_like(self.position)