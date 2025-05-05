import numpy as np
import random
from typing import List, Tuple, Optional, Callable, Union, Any
from scipy.spatial.distance import cosine
from multiprocessing import Pool, cpu_count
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
        discrete_dims: Optional[List[int]] = None
    ):
        self.objective_func = objective_func
        self.problem_dim = problem_dim
        self.n_particles = n_particles
        self.bounds = bounds if bounds else [(-5, 5)] * problem_dim
        self.multi_objective = multi_objective
        self.use_parallel = use_parallel
        self.init_method = init_method
        self.discrete_dims = discrete_dims or []
        # 势垒高度自适应（单峰函数降低）
        self.barrier_height = 0.3 if self._is_unimodal() else barrier_height
        # 初始化粒子群并加入个体最优记录
        self.particles = []
        for _ in range(n_particles):
            p = QuantumParticle(problem_dim, self.discrete_dims)
            p.init_random_position(self.bounds, method=self.init_method)
            p.velocity = np.zeros(problem_dim)
            p.best_fitness = float('inf')
            p.best_position = p.position.copy()
            self.particles.append(p)
        # 全局最优初始化
        self.global_best_pos = None
        self.global_best_fit = float('inf') if not multi_objective else []
        # 物理参数与模型参数
        self.temperature = temperature
        self.p_innovate = 0.1
        self.q_imitate = 0.5
        self.entropy_threshold = entropy_threshold
        # 日志与多样性监控
        self.diversity_history = []
        self.history = []
        # 多目标：外部档案用于保存非支配解
        if self.multi_objective:
            self.archive = []

    def _evaluate_fitness(self):
        """评估粒子适应度（带并行计算）"""
        positions = [p.position.copy() for p in self.particles]
        if self.use_parallel:
            with Pool(cpu_count()) as pool:
                fits = pool.map(self.objective_func, positions)
        else:
            fits = [self.objective_func(pos) for pos in positions]
        for p, fit in zip(self.particles, fits):
            p.fitness = fit
            # 更新个体最优
            if (not self.multi_objective and fit < p.best_fitness) or self.multi_objective:
                p.best_fitness = fit
                p.best_position = p.position.copy()
            # 更新全局最优
            if self.multi_objective:
                self._update_pareto_front(p)
            else:
                if fit < self.global_best_fit:
                    self.global_best_fit = fit
                    self.global_best_pos = p.position.copy()
        # 如果未找到任何有效解，则设置默认全局最优位置
        if self.global_best_pos is None and len(positions) > 0:
            self.global_best_pos = np.mean(positions, axis=0)
        self._update_diversity()
        self._restart_if_stagnant()
        self._differential_mutation()  # 差分变异增强多样性
        self._memory_perturbation()    # 记忆扰动防止陷入局部极值
        self.history.append({
            'iteration': len(self.history),
            'best_fitness': self.global_best_fit if not self.multi_objective else None,
            'avg_fitness': np.mean(fits),
            'diversity': self._calculate_diversity()
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
        # 单峰函数更快降温
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
                    p.init_random_position(self.bounds, method='lhs')  # 使用LHS提高分布质量
                    p.collapsed = False
                    p.state = None

    def _fine_tune_development(self, particle):
        if isinstance(particle.state, ExploitationState):
            max_iter = len(self.history) + 1
            iter_factor = 1 - (len(self.history) / max_iter)
            mutation = np.random.normal(0, 0.01 * iter_factor, self.problem_dim)
            particle.position += mutation
            particle.set_position(particle.position, self.bounds)

    def _differential_mutation(self, F=0.5, CR=0.9):
        if random.random() < 0.1:
            for i, p in enumerate(self.particles):
                idxs = [idx for idx in range(self.n_particles) if idx != i]
                a, b = np.random.choice(idxs, 2, replace=False)
                donor = self.particles[a].position + F * (
                    self.particles[b].position - p.position
                )
                trial = np.where(np.random.rand(self.problem_dim) < CR, donor, p.position)
                trial_fit = self.objective_func(trial)
                if trial_fit < p.fitness:
                    p.position = trial
                    p.fitness = trial_fit

    def _memory_perturbation(self):
        # 后期加入记忆扰动机制，帮助跳出局部最优
        if len(self.history) > 0.8 * 100:  # 假设 max_iter 是 100
            for p in self.particles:
                if random.random() < 0.05:
                    perturb = np.random.uniform(-0.5, 0.5, self.problem_dim)
                    new_pos = p.position + perturb
                    p.set_position(new_pos, self.bounds)

    def _tabu_jump(self):
        # 类似禁忌搜索的跳跃机制，用于 Ackley/Michalewicz 等问题
        if len(self.history) % 20 == 0 and len(self.history) > 0:
            best_idx = np.argmin([p.fitness for p in self.particles])
            best_particle = self.particles[best_idx]
            jump_dir = np.random.randn(self.problem_dim)
            jump_dir /= np.linalg.norm(jump_dir) + 1e-8
            jump_step = 1.0
            new_pos = best_particle.position + jump_dir * jump_step
            best_particle.set_position(new_pos, self.bounds)

    def _local_search(self, particle):
        def obj(x):
            return self.objective_func(x)
        res = minimize(obj, particle.position, bounds=self.bounds, method='L-BFGS-B')
        if res.success and res.fun < particle.fitness:
            particle.position = res.x
            particle.fitness = res.fun

    def _is_unimodal(self, num_samples=50, threshold=0.1):
        if "Sphere" or "Rastrigin" in self.objective_func.__name__:  
            return True
        # 生成随机样本点
        samples = np.array([self._sample_in_bounds() for _ in range(num_samples)])
        
        # 获取对应的目标函数值
        fits = np.array([self.objective_func(x) for x in samples])

        # 找出最小值附近的点
        best_idx = np.argmin(fits)
        best_point = samples[best_idx]
        best_value = fits[best_idx]

        # 检查其他点是否都朝着这个最小值方向下降（无多个局部最优）
        for i in range(num_samples):
            if i == best_idx:
                continue
            # 计算当前点与最优值的差异
            diff = fits[i] - best_value
            if diff > threshold:  # 如果差异超过阈值，则认为存在局部极小值
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
                p.set_position(new_pos, self.bounds)
                if len(self.particles) > 1:
                    others = [x for x in self.particles if x != p]
                    partner = random.choice(others)
                    new_dim = self._cultural_crossover(p, partner)
                    p.cultural_dimension = new_dim
                self._fine_tune_development(p)
            self._evaluate_fitness()
            self._tabu_jump()
            # 后期局部搜索
            if iter > max_iter * 0.7:
                # 获取当前排名前 top_k 的粒子
                top_k = 3
                sorted_particles = sorted(self.particles, key=lambda p: p.fitness)
                candidates = sorted_particles[:top_k]

                # 添加一个随机粒子增加探索性（概率触发）
                if random.random() < 0.3:
                    candidates.append(random.choice(self.particles))

                # 缓存已搜索过的位置，防止重复搜索
                if not hasattr(self, 'searched_positions'):
                    self.searched_positions = set()

                for p in candidates:
                    pos_tuple = tuple(np.round(p.position, 5))
                    if pos_tuple not in self.searched_positions:
                        self._local_search(p)
                        self.searched_positions.add(pos_tuple)
            print(f"Iteration {iter+1}/{max_iter}, Best Fitness: {self.global_best_fit}")
            if callback:
                callback(self)

    def get_best_solution(self):
        if self.multi_objective:
            return np.array([p.position for p in self.global_best_fit])
        else:
            return self.global_best_pos

    # TODO: 在离散方面使用更好的算法进行优化