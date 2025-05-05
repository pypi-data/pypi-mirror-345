import numpy as np
import random
from typing import List, Tuple, Optional, Callable, Union
from scipy.spatial.distance import cosine
from concurrent.futures import ProcessPoolExecutor
from scipy.optimize import minimize
from .particle import QuantumParticle, ExplorationState, ExploitationState


class SEDOptimizer:
    def __init__(
        self,
        objective_func: Callable[[np.ndarray], Union[float, List[float]]],
        problem_dim: int,
        n_particles: int = 30,
        barrier_height: float = 0.5,
        entropy_threshold: float = 0.7,
        temperature: float = 1.0,
        bounds: Optional[List[Tuple[float, float]]] = None,
        multi_objective: bool = False,
        use_parallel: bool = True,
        init_method: str = 'uniform',
        discrete_dims: Optional[List[int]] = None,
        is_permutation: bool = False  # 新增参数
    ):
        self.objective_func = objective_func
        self.problem_dim = problem_dim
        self.n_particles = n_particles
        self.bounds = bounds if bounds else [(-5, 5)] * problem_dim
        self.multi_objective = multi_objective
        self.use_parallel = use_parallel
        self.init_method = init_method
        self.discrete_dims = discrete_dims or []
        self.is_permutation = is_permutation  # 是否为排列型问题

        self.barrier_height = 0.3 if self._is_unimodal() else barrier_height

        self.particles = []
        for _ in range(n_particles):
            p = QuantumParticle(problem_dim, self.discrete_dims)
            if self.is_permutation:
                p.position = np.random.rand(problem_dim)
            else:
                p.init_random_position(self.bounds, method=self.init_method)
            p.velocity = np.zeros(problem_dim)
            p.best_fitness = float('inf') if not multi_objective else []
            p.best_position = p.position.copy()
            self.particles.append(p)

        self.global_best_pos = None
        self.global_best_fit = float('inf') if not multi_objective else []

        self.temperature = temperature
        self.p_innovate = 0.1
        self.q_imitate = 0.5
        self.entropy_threshold = entropy_threshold

        self.diversity_history = []
        self.history = []

        if self.multi_objective:
            self.archive = []

    def _evaluate_fitness(self):
        positions = []
        decoded_routes = []

        for p in self.particles:
            if self.is_permutation:
                route = np.argsort(p.position).astype(int)
                decoded_routes.append(route)
                positions.append(route)
            else:
                pos = p.position.copy()
                positions.append(pos)
                decoded_routes.append(pos)

        if self.use_parallel:
            with ProcessPoolExecutor() as executor:
                fits = list(executor.map(self.objective_func, decoded_routes))
        else:
            fits = [self.objective_func(route) for route in decoded_routes]

        for p, fit in zip(self.particles, fits):
            p.fitness = fit
            if not self.multi_objective:
                if fit < p.best_fitness:
                    p.best_fitness = fit
                    p.best_position = p.position.copy()
            else:
                if self._is_dominated(fit, p.best_fitness) or not p.best_fitness:
                    p.best_fitness = fit
                    p.best_position = p.position.copy()

            if not self.multi_objective:
                if fit < self.global_best_fit:
                    self.global_best_fit = fit
                    self.global_best_pos = p.position.copy()
            else:
                self._update_pareto_front(p)

        if self.global_best_pos is None and len(positions) > 0:
            self.global_best_pos = np.mean(positions, axis=0)

        self._update_diversity()
        self._restart_if_stagnant()
        self._differential_mutation()
        self._memory_perturbation()
        avg_fit = np.mean([f if not self.multi_objective else f[0] for f in fits])
        diversity = self._calculate_diversity()
        self.history.append({
            'iteration': len(self.history),
            'best_fitness': self.global_best_fit if not self.multi_objective else None,
            'avg_fitness': avg_fit,
            'diversity': diversity
        })

    def _is_dominated(self, fit1, fit2):
        return all(f1 <= f2 for f1, f2 in zip(fit1, fit2))

    def _update_pareto_front(self, particle):
        to_remove = []
        dominated = False
        for other in self.global_best_fit:
            if self._is_dominated(other.fitness, particle.fitness):
                dominated = True
                break
            if self._is_dominated(particle.fitness, other.fitness):
                to_remove.append(other)
        if not dominated:
            self.global_best_fit = [p for p in self.global_best_fit if p not in to_remove]
            self.global_best_fit.append(particle)
        self.archive = self.global_best_fit

    def _cultural_similarity(self, p1, p2):
        return 1 - cosine(p1.cultural_dimension, p2.cultural_dimension)

    def _calculate_entropy_flow(self, particle, neighbors):
        total_flow = 0j
        for neighbor in neighbors:
            sim = self._cultural_similarity(particle, neighbor)
            distance = 1 - sim
            tunnel = np.exp(-self.barrier_height * distance)
            flow = particle.entropy_phase * np.conj(neighbor.entropy_phase) * tunnel
            total_flow += flow
        return total_flow

    def _dynamic_collapse(self):
        diversity = self._calculate_diversity()
        self.temperature = max(0.05, 1.0 - (diversity * 1.2 if self._is_unimodal() else 0.8))
        for p in self.particles:
            entropy_diff = abs(p.positive_entropy - p.negative_entropy)
            if entropy_diff > self.entropy_threshold:
                delta_e = p.fitness - self.global_best_fit if not self.multi_objective else 0
                probability = 1 / (np.exp((delta_e / (self.temperature + 1e-6))) + 1)
                if random.random() < probability:
                    p.state = ExploitationState()
                else:
                    p.state = ExplorationState()
                p.collapsed = True

    def _cultural_crossover(self, p1, p2):
        child_dim = []
        for i in range(6):  # 六个文化维度
            if random.random() < 0.7:
                chosen = max(p1.cultural_dimension[i], p2.cultural_dimension[i])
                child_dim.append(chosen)
            else:
                mutation = p1.cultural_dimension[i] + np.random.normal(0, 0.1)
                child_dim.append(mutation)
        return np.array(child_dim)

    def _update_bass_model(self, curr_iter, max_iter):
        progress = curr_iter / max_iter
        self.p_innovate = 0.2 * (1 - progress)**2
        self.q_imitate = 0.5 * (1 + np.sqrt(progress))

    def _calculate_diversity(self):
        positions = np.array([p.position for p in self.particles])
        mean_pos = np.mean(positions, axis=0)
        return np.mean(np.linalg.norm(positions - mean_pos, axis=1))

    def _update_diversity(self):
        self.diversity_history.append(self._calculate_diversity())

    def _restart_if_stagnant(self, threshold=0.001, window=5):
        if len(self.diversity_history) >= window:
            recent = self.diversity_history[-window:]
            if max(recent) - min(recent) < threshold:
                print("Diversity too low, restarting particles...")
                restart_ratio = 0.3 if self._is_unimodal() else 0.2
                for p in random.sample(self.particles, int(self.n_particles * restart_ratio)):
                    if self.is_permutation:
                        p.position = np.random.rand(self.problem_dim)
                    else:
                        p.init_random_position(self.bounds, method='lhs')
                    p.collapsed = False
                    p.state = None

    def _fine_tune_development(self, particle):
        if isinstance(particle.state, ExploitationState):
            max_iter = len(self.history) + 1
            iter_factor = 1 - (len(self.history) / max_iter)
            mutation = np.random.normal(0, 0.01 * iter_factor, self.problem_dim)
            particle.position += mutation
            if self.is_permutation:
                particle.position = np.clip(particle.position, 0, 1)
            else:
                particle.set_position(particle.position, self.bounds)

    def _differential_mutation(self, F=0.5, CR=0.9):
        pass  # 不适用于排列问题

    def _memory_perturbation(self):
        if len(self.history) > 0.8 * 100:
            for p in self.particles:
                if random.random() < 0.05:
                    perturb = np.random.uniform(-0.1, 0.1, self.problem_dim)
                    new_pos = p.position + perturb
                    if self.is_permutation:
                        p.position = np.clip(new_pos, 0, 1)
                    else:
                        p.set_position(new_pos, self.bounds)

    def _tabu_jump(self):
        pass  # 可选实现

    def _local_search_2opt(self, particle):
        """
        使用 2-opt 算法对排列型解进行局部优化
        :param particle: 当前粒子
        """
        if not self.is_permutation:
            return

        route = np.argsort(particle.position).astype(int)
        best_route = route.copy()
        best_fitness = self.objective_func(best_route)

        improved = True
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    new_route = self._two_opt_swap(best_route, i, j)
                    new_fitness = self.objective_func(new_route)

                    # 单目标优化
                    if not self.multi_objective:
                        if new_fitness < best_fitness:
                            best_route = new_route
                            best_fitness = new_fitness
                            improved = True
                    # 多目标优化
                    else:
                        if self._is_dominated(new_fitness, best_fitness) and not self._is_dominated(best_fitness, new_fitness):
                            best_route = new_route
                            best_fitness = new_fitness
                            improved = True
            if improved:
                particle.position = np.random.rand(self.problem_dim)
                particle.position[best_route] += np.linspace(0, 1, len(best_route)) * 0.01  # 微调以保持顺序
                particle.fitness = best_fitness

    def _two_opt_swap(self, route, i, j):
        """执行一次 2-opt swap"""
        new_route = np.copy(route)
        new_route[i:j+1] = new_route[i:j+1][::-1]
        return new_route

    def _is_unimodal(self, num_samples=50, threshold=0.1):
        if self.multi_objective:
            return False
        if "Sphere" in self.objective_func.__name__ or "Rastrigin" in self.objective_func.__name__:
            return True
        samples = np.array([self._sample_in_bounds() for _ in range(num_samples)])
        fits = np.array([self.objective_func(x) for x in samples])
        best_idx = np.argmin(fits)
        best_value = fits[best_idx]
        for i in range(num_samples):
            if i == best_idx:
                continue
            diff = fits[i] - best_value
            if diff > threshold:
                return False
        return True

    def _sample_in_bounds(self):
        return np.array([
            np.random.uniform(low, high) for low, high in self.bounds
        ])

    def optimize(self, max_iter, callback=None):
        self._evaluate_fitness()
        for iter in range(max_iter):
            self._update_bass_model(iter, max_iter)
            for i, p in enumerate(self.particles):
                neighbors = self.particles[:i] + self.particles[i+1:]
                flow = self._calculate_entropy_flow(p, neighbors)
                p.positive_entropy += np.real(flow) * 0.01
                p.negative_entropy += np.imag(flow) * 0.01
                p.positive_entropy = np.clip(p.positive_entropy, 0, 1)
                p.negative_entropy = np.clip(p.negative_entropy, 0, 1)
            self._dynamic_collapse()
            for p in self.particles:
                if p.collapsed:
                    if isinstance(p.state, ExploitationState):
                        cognitive = 2.0 * random.random() * (p.best_position - p.position)
                        social = 2.0 * random.random() * (self.global_best_pos - p.position)
                        p.velocity = 0.7 * p.velocity + cognitive + social
                    else:
                        partner = random.choice(self.particles)
                        social = 2.0 * random.random() * (partner.position - p.position)
                        p.velocity = 0.7 * p.velocity + social
                else:
                    if random.random() < 0.5:
                        p.velocity = 0.5 * p.velocity + np.random.uniform(-1, 1, self.problem_dim)
                    else:
                        cognitive = 1.0 * random.random() * (self.global_best_pos - p.position)
                        p.velocity = 0.5 * p.velocity + cognitive
                new_pos = p.position + p.velocity
                if self.is_permutation:
                    p.position = np.clip(new_pos, 0, 1)
                else:
                    p.set_position(new_pos, self.bounds)
                if len(self.particles) > 1:
                    others = [x for x in self.particles if x != p]
                    partner = random.choice(others)
                    new_dim = self._cultural_crossover(p, partner)
                    p.cultural_dimension = new_dim
                self._fine_tune_development(p)

            self._evaluate_fitness()
          # 后期阶段启用局部搜索
            if iter > int(max_iter * 0.7):
                top_k = 5
                sorted_particles = sorted(self.particles, key=lambda x: x.fitness if not self.multi_objective else sum(x.fitness))
                candidates = sorted_particles[:top_k]
                for p in candidates:
                    self._local_search_2opt(p)
                self._evaluate_fitness()
            print(f"Iteration {iter+1}/{max_iter}, Best Fitness: {self.global_best_fit}")
            if callback:
                callback(self)


    def _remove_duplicate_solutions(self, solutions):
        """
        过滤重复解（支持浮点数和整数）
        :param solutions: list of objects (list/tuple/np.ndarray)
        :return: 去重后的解
        """
        seen = set()
        unique_solutions = []
        for sol in solutions:
            # 如果是 numpy 数组，保留五位小数防止浮点误差，并将 np.int64 转换为 int
            if isinstance(sol, np.ndarray):
                key = tuple(np.round(sol, 5).astype(int))
            elif isinstance(sol, list):
                key = tuple(map(lambda x: round(x, 5) if isinstance(x, float) else int(x), sol))
            else:
                key = sol
            if key not in seen:
                seen.add(key)
                unique_solutions.append(sol)
        return unique_solutions


    def get_best_solution(self):
        if self.multi_objective:
            raw_solutions = [p.fitness for p in self.global_best_fit]
            return self._remove_duplicate_solutions(raw_solutions)
        elif self.is_permutation:
            return np.argsort(self.global_best_pos).astype(int)
        else:
            return self.global_best_pos

# TODO: 离散型优化问题：
# Rastrigin与Michalewicz函数的适应度不良