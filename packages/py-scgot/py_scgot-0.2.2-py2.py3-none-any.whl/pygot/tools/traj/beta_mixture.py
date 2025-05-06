import numpy as np
from scipy.stats import beta
from scipy.optimize import minimize
from scipy.stats import ks_2samp
import pandas as pd  # 需要用到Pandas处理结果

# 用拟合好的Beta Mixture Model生成新的样本
def generate_samples(n_samples, params, random_state=None):
    rng = np.random.default_rng(random_state)
    samples = []
    weights = params[:, 2]
    weights = weights / weights.sum()  
    for _ in range(n_samples):
        component = rng.choice(len(weights), p=weights)
        alpha, beta_param, _ = params[component]
        sample = beta.rvs(alpha, beta_param, random_state=rng)
        samples.append(sample)
    return np.array(samples)

def initialize_parameters(k, a_b=100, random_state=None):
    rng = np.random.default_rng(random_state)
    params = []
    ratio = np.linspace(0.05, 0.95, k)
    for i in range(k):
        alpha = a_b * ratio[i]  # 避免过小值
        beta_param = a_b * (1 - ratio[i])  # 避免过小值
        weight = 1.0 / k
        params.append([alpha, beta_param, weight])
    return np.array(params)

# 计算样本属于每个贝塔分布的概率
def e_step(data, params):
    responsibilities = np.zeros((data.size, params.shape[0]))
    for i, (alpha, beta_param, weight) in enumerate(params):
        responsibilities[:, i] = weight * beta.pdf(data, alpha, beta_param + 1e-10)  # 增加数值稳定性
    responsibilities = responsibilities / (responsibilities.sum(axis=1, keepdims=True) + 1e-10)  # 防止除零
    return responsibilities

# 计算对数似然值
def log_likelihood(data, params):
    log_lik = 0
    for alpha, beta_param, weight in params:
        log_lik += weight * beta.pdf(data, alpha, beta_param + 1e-10)
    return np.sum(np.log(log_lik + 1e-10))  # 增加数值稳定性

# 更新贝塔混合模型参数
def m_step(data, responsibilities, params):
    new_params = []
    for i in range(responsibilities.shape[1]):
        weight = responsibilities[:, i].sum() / data.size
        alpha, beta_param = update_beta_params(data, responsibilities[:, i], params[i, :2])
        new_params.append([alpha, beta_param, weight])
    return np.array(new_params)

# 更新贝塔分布的形状参数
def update_beta_params(data, resp, x0=None):
    def objective(params):
        alpha, beta_param = params
        # 增加数值稳定性，避免log(0)
        return -np.sum(resp * np.log(beta.pdf(data, alpha, beta_param) + 1e-10))

    if x0 is None:
        x0 = [1., 1.]
    result = minimize(objective, x0=x0, bounds=[(1e-4, None), (1e-4, None)])  # 确保参数非零
    return result.x

# EM算法主循环
def fit_beta_mixture(data, k, n_iters, tol=1e-4, random_state=None):
    params = initialize_parameters(k, random_state=random_state)
    log_likelihoods = []

    for i in range(n_iters):
        responsibilities = e_step(data, params)
        params = m_step(data, responsibilities, params)
        
        # 计算当前对数似然值
        curr_log_likelihood = log_likelihood(data, params)
        log_likelihoods.append(curr_log_likelihood)
        
        # 检查收敛性
        if i > 0 and np.abs(log_likelihoods[-1] - log_likelihoods[-2]) < tol:
            print(f"Converged at iteration {i}.")
            break
        
    return params, responsibilities


def suggest_best_split_k(adata, time_key, k_range=range(3, 10), n_iters=100):
    np.random.seed(0)  
    data = adata.obs[time_key].to_numpy() * 0.9 + 0.05
    res_df = []
    responsibilities_list = []
    params_list = []
    for k in k_range:
        print('fitting k: {}'.format(k))
        params, responsibilities = fit_beta_mixture(data, k, n_iters, random_state=0)
        generated_samples = generate_samples(len(data), params, random_state=0)
        ks_stat, p_value = ks_2samp(data, generated_samples)
        responsibilities_list.append(responsibilities)
        params_list.append(params)
        res_df.append([k, ks_stat])
    res_df = pd.DataFrame(res_df, columns=['k', 'ks-stats']).sort_values('ks-stats')
    return res_df, responsibilities_list, params_list