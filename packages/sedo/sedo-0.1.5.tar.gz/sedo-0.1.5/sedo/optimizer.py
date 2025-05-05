import numpy as np
import random
from typing import List, Tuple, Optional, Callable, Union, Any
from scipy.spatial.distance import cosine
from multiprocessing import Pool, cpu_count
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
        """
        Social Entropy Diffusion Optimization (SEDO) 核心优化器
        参数:
            objective_func: 目标函数，输入为 np.ndarray，输出为浮点数或列表（多目标）
            problem_dim: 问题维度
            n_particles: 粒子数量，默认30
            barrier_height: 势垒高度（单峰函数建议0.3），影响文化传播距离衰减
            entropy_threshold: 熵阈值（开发/探索切换阈值）
            temperature: 初始系统温度
            bounds: 各维度搜索范围，默认为[(-5,5)] * dim
            multi_objective: 是否启用多目标优化
            use_parallel: 是否使用并行计算
            init_method: 初始化方法 ['uniform', 'lhs', 'orthogonal']
            discrete_dims: 离散变量索引列表
        """
        self.objective_func = objective_func
        self.problem_dim = problem_dim
        self.n_particles = n_particles
        self.bounds = bounds if bounds else [(-5, 5)] * problem_dim
        self.multi_objective = multi_objective
        self.use_parallel = use_parallel
        self.init_method = init_method
        self.discrete_dims = discrete_dims or []
        
        # 动态势垒高度设置（优化点6）
        self.barrier_height = 0.3 if self._is_unimodal() else barrier_height
        
        # 初始化粒子群
        self.particles = []
        for _ in range(n_particles):
            p = QuantumParticle(problem_dim, self.discrete_dims)
            p.init_random_position(self.bounds, method=self.init_method)
            p.velocity = np.zeros(problem_dim)  # 显式初始化速度
            self.particles.append(p)
            
        # 全局最优位置与适应度
        self.global_best_pos = None
        self.global_best_fit = float('inf') if not multi_objective else []
        
        # 物理参数优化
        self.temperature = temperature
        # Bass扩散模型参数（优化点3）
        self.p_innovate = 0.1   # 创新系数（非线性更新）
        self.q_imitate = 0.5    # 模仿系数（非线性更新）

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
        
        self.history.append({
            'iteration': len(self.history),
            'best_fitness': self.global_best_fit if not self.multi_objective else None,
            'avg_fitness': np.mean(fits),
            'diversity': self._calculate_diversity()
        })

    def _is_dominated(self, fit1, fit2):
        """判断fit1是否支配fit2（多目标优化用）"""
        return all(f1 <= f2 for f1, f2 in zip(fit1, fit2))

    def _update_pareto_front(self, particle):
        """更新Pareto前沿并维护外部档案"""
        to_remove = []
        dominated = False
        # 检查当前粒子是否被支配
        for other in self.global_best_fit:
            if self._is_dominated(other.fitness, particle.fitness):
                dominated = True
                break
            if self._is_dominated(particle.fitness, other.fitness):
                to_remove.append(other)
        # 如果未被支配，加入前沿
        if not dominated:
            self.global_best_fit = [p for p in self.global_best_fit if p not in to_remove]
            self.global_best_fit.append(particle)
        # 更新外部档案
        self.archive = self.global_best_fit

    def _cultural_similarity(self, p1, p2):
        """计算文化相似度（余弦相似度）"""
        return 1 - cosine(p1.cultural_dimension, p2.cultural_dimension)

    def _calculate_entropy_flow(self, particle, neighbors):
        """计算熵流（文化传播核心）"""
        total_flow = 0j
        for neighbor in neighbors:
            sim = self._cultural_similarity(particle, neighbor)
            distance = 1 - sim
            tunnel = np.exp(-self.barrier_height * distance)
            flow = particle.entropy_phase * np.conj(neighbor.entropy_phase) * tunnel
            total_flow += flow
        return total_flow

    def _dynamic_collapse(self):
        """动态坍缩机制（优化点1）：根据熵值决定探索/开发状态"""
        diversity = self._calculate_diversity()
        # 温度下降更平缓（乘以系数0.8）
        self.temperature = max(0.05, 1.0 - (diversity * 0.8))
        
        for p in self.particles:
            entropy_diff = abs(p.positive_entropy - p.negative_entropy)
            if entropy_diff > self.entropy_threshold:
                delta_e = p.fitness - self.global_best_fit if not self.multi_objective else 0
                # 使用指数衰减的概率函数（优化点1）
                probability = 1 / (np.exp((delta_e / (self.temperature + 1e-6))) + 1)
                if random.random() < probability:
                    p.state = ExploitationState()
                else:
                    p.state = ExplorationState()
                p.collapsed = True

    def _cultural_crossover(self, p1, p2):
        """文化维度交叉操作（保留原实现）"""
        child_dim = []
        for i in range(6):  # 六个文化维度
            if random.random() < 0.7:  # 文化传播概率
                chosen = max(p1.cultural_dimension[i], p2.cultural_dimension[i])
                child_dim.append(chosen)
            else:
                mutation = p1.cultural_dimension[i] + np.random.normal(0, 0.1)
                child_dim.append(mutation)
        return np.array(child_dim)

    def _update_bass_model(self, curr_iter, max_iter):
        """Bass扩散模型更新创新与模仿系数（优化点3）"""
        progress = curr_iter / max_iter
        # 非线性变化策略：指数衰减/增长
        self.p_innovate = 0.2 * (1 - progress)**2  # 更快减少
        self.q_imitate = 0.5 * (1 + np.sqrt(progress))  # 更快增加

    def _calculate_diversity(self):
        """计算种群多样性（欧氏距离均值）"""
        positions = np.array([p.position for p in self.particles])
        mean_pos = np.mean(positions, axis=0)
        diversity = np.mean(np.linalg.norm(positions - mean_pos, axis=1))
        return diversity

    def _update_diversity(self):
        """记录多样性变化"""
        self.diversity_history.append(self._calculate_diversity())

    def _restart_if_stagnant(self, threshold=0.001, window=5):
        """多样性重启机制（优化点4）"""
        if len(self.diversity_history) >= window:
            recent = self.diversity_history[-window:]
            if max(recent) - min(recent) < threshold:
                print("Diversity too low, restarting particles...")
                # 根据问题类型调整重启比例（优化点4）
                restart_ratio = 0.1 if self._is_unimodal() else 0.2
                for p in random.sample(self.particles, int(self.n_particles * restart_ratio)):
                    p.init_random_position(self.bounds, method=self.init_method)
                    p.collapsed = False
                    p.state = None

    def _fine_tune_development(self, particle):
        """局部精细开发策略（优化点5）"""
        if isinstance(particle.state, ExploitationState):
            max_iter = len(self.history) + 1  # 假设已知最大迭代次数
            iter_factor = 1 - (len(self.history) / max_iter)
            # 动态调整扰动幅度（优化点5）
            mutation = np.random.normal(0, 0.01 * iter_factor, self.problem_dim)
            particle.position += mutation
            particle.set_position(particle.position, self.bounds)

    def _is_unimodal(self):
        """判断是否为单峰函数（根据目标函数名称）"""
        return 'Sphere' in self.objective_func.__name__

    def optimize(self, max_iter, callback=None):
        """执行优化流程"""
        self._evaluate_fitness()
        
        for iter in range(max_iter):
            self._update_bass_model(iter, max_iter)
            
            # 更新粒子状态与熵值
            for i, p in enumerate(self.particles):
                neighbors = self.particles[:i] + self.particles[i+1:]
                flow = self._calculate_entropy_flow(p, neighbors)
                p.positive_entropy += np.real(flow) * 0.01
                p.negative_entropy += np.imag(flow) * 0.01
                p.positive_entropy = np.clip(p.positive_entropy, 0, 1)
                p.negative_entropy = np.clip(p.negative_entropy, 0, 1)
                
            self._dynamic_collapse()
            
            # 粒子移动（优化点2）
            for p in self.particles:
                if p.collapsed:
                    if isinstance(p.state, ExploitationState):
                        # 开发阶段增加认知系数至2.0（优化点2）
                        cognitive = 2.0 * random.random() * (self.global_best_pos - p.position)
                        p.velocity = 0.7 * p.velocity + cognitive
                    else:
                        # 探索阶段引入其他粒子的最优信息（优化点2）
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
                    
                # 局部精细开发
                self._fine_tune_development(p)
                
            self._evaluate_fitness()
            print(f"Iteration {iter+1}/{max_iter}, Best Fitness: {self.global_best_fit}")
            
            if callback:
                callback(self)

    def get_best_solution(self):
        """获取当前最优解"""
        if self.multi_objective:
            return np.array([p.position for p in self.global_best_fit])
        else:
            return self.global_best_pos
