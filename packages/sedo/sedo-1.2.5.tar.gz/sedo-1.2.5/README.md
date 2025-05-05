# 社会熵扩散优化算法(SEDO) / Social Entropy Diffusion Optimizer (SEDO)

[[English]](#english-version) | [[中文]](#chinese-version) | [[开发文档]](sedo/docs/development.md)

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

<a id="chinese-version"></a>

受社会学与量子物理启发的创新型全局优化算法

### 算法特点

- 🌐 文化空间信息传播模型
- ⚛️ 量子化粒子表示
- 🔥 基于熵流的探索-开发平衡
- 🎯 支持单目标/多目标优化
- ⚡ 并行计算加速

### 安装方法

```bash
pip install sedo
```

### 快速开始
**不要使用 lambda 函数作为目标函数！**
```python
from sedo import SEDOptimizer

# 定义目标函数
def rastrigin(x):
    return 10*len(x) + sum(x**2 - 10*np.cos(2*np.pi*x))

# 初始化优化器
optimizer = SEDOptimizer(
    objective_func=rastrigin,
    problem_dim=20,
    n_particles=50
)

# 执行优化
optimizer.optimize(max_iter=200)

# 获取结果
best_solution = optimizer.get_best_solution()
print(f"最优解: {best_solution}")
```

### 对比测试结果

| 函数         | 算法 | 平均适应度     | 标准差        |
|-------------|------|--------------|------------|
| Sphere      | SEDO | 0.105087     | 0.057231   |
| Sphere      | PSO  | 0.097989     | 0.080966   |
| Rosenbrock  | SEDO | -25124.000000| 531.337934 |
| Rosenbrock  | PSO  | -24136.000000| 1778.088862|
| Ackley      | SEDO | 1.739894     | 0.821921   |
| Ackley      | PSO  | 2.284575     | 0.898855   |


### 高级特性

#### 文化传播可视化
```python
from sedo.utils import plot_cultural_diffusion
plot_cultural_diffusion(optimizer.particles)
```

#### 参数敏感性分析
```python
from sedo.utils import parameter_sensitivity
results = parameter_sensitivity(
    objective_func,
    param_ranges={
        'barrier_height': (0.1, 1.0),
        'entropy_threshold': (0.3, 0.9)
    }
)
```

### 应用案例

1. **神经网络超参数优化**
```python
optimizer = SEDOptimizer(
    objective_func=neural_net_train,
    problem_dim=8,
    bounds=[(32,512), (0.0001,0.1), ...]  # 各参数范围
)
```

2. **投资组合优化**
```python
optimizer = SEDOptimizer(
    objective_func=portfolio_eval,
    problem_dim=10,
    multi_objective=True  # 同时优化收益和风险
)
```

### 参与贡献

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送分支 (`git push origin feature/your-feature`)
5. 新建Pull Request

### 许可证

MIT License

<a id="english-version"></a>
## Social Entropy Diffusion Optimizer (SEDO)

[[English]](#english-version) | [[中文]](#chinese-version) | [[Development Documentation]](sedo/docs/development.md)

An innovative global optimization algorithm inspired by sociology and quantum physics

### Key Features

- 🌐 Cultural space information diffusion model
- ⚛️ Quantum particle representation
- 🔥 Exploration-exploitation balance based on entropy flow
- 🎯 Single/Multi-objective optimization support
- ⚡ Parallel computing acceleration

### Installation

```bash
pip install sedo
```

### Quick Start

**Do Not USE lambda function as objective function!**
```python
from sedo import SEDOptimizer

# Define objective function
def rastrigin(x):
    return 10*len(x) + sum(x**2 - 10*np.cos(2*np.pi*x))

# Initialize optimizer
optimizer = SEDOptimizer(
    objective_func=rastrigin,
    problem_dim=20,
    n_particles=50
)

# Run optimization
optimizer.optimize(max_iter=200)

# Get results
best_solution = optimizer.get_best_solution()
print(f"Optimal solution: {best_solution}")
```

### Comparative Test Results
| Function         | Algorithm | Avg Fitness      | Std Dev        |
|-------------|------|--------------|------------|
| Sphere      | SEDO | 0.105087     | 0.057231   |
| Sphere      | PSO  | 0.097989     | 0.080966   |
| Rosenbrock  | SEDO | -25124.000000| 531.337934 |
| Rosenbrock  | PSO  | -24136.000000| 1778.088862|
| Ackley      | SEDO | 1.739894     | 0.821921   |
| Ackley      | PSO  | 2.284575     | 0.898855   |


### Advanced Features

#### Cultural Diffusion Visualization
```python
from sedo.utils import plot_cultural_diffusion
plot_cultural_diffusion(optimizer.particles)
```

#### Parameter Sensitivity Analysis
```python
from sedo.utils import parameter_sensitivity
results = parameter_sensitivity(
    objective_func,
    param_ranges={
        'barrier_height': (0.1, 1.0),
        'entropy_threshold': (0.3, 0.9)
    }
)
```

### Application Examples

1. **Neural Network Hyperparameter Tuning**
```python
optimizer = SEDOptimizer(
    objective_func=neural_net_train,
    problem_dim=8,
    bounds=[(32,512), (0.0001,0.1), ...]  # Parameter ranges
)
```

2. **Portfolio Optimization**
```python
optimizer = SEDOptimizer(
    objective_func=portfolio_eval,
    problem_dim=10,
    multi_objective=True  # Optimize return and risk simultaneously
)
```

### How to Contribute

We welcome issues and pull requests!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

### License

MIT License

[Back to Top](#社会熵扩散优化算法sedo--social-entropy-diffusion-optimizer-sedo)
