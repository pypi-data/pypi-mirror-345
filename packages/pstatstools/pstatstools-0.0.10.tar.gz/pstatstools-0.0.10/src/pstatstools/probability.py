import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Union, Optional, Any, Callable

def binomial_probability(k: Union[int, List[int]], n: int, p: float, 
                       cumulative: bool = False, 
                       lower_tail: bool = True) -> Union[float, np.ndarray]:
    """Calculate binomial probability
    
    Parameters:
    -----------
    k : int or list of int
        Number of successes
    n : int
        Number of trials
    p : float
        Probability of success in a single trial
    cumulative : bool, optional
        If True, calculate cumulative probability. Default is False.
    lower_tail : bool, optional
        If True, calculate P(X ≤ k) for cumulative; otherwise P(X > k). Default is True.
        
    Returns:
    --------
    float or numpy.ndarray : Probability or probabilities
    """
    if cumulative:
        if lower_tail:
            return stats.binom.cdf(k, n, p)
        else:
            return stats.binom.sf(k, n, p)
    else:
        return stats.binom.pmf(k, n, p)


def poisson_probability(k: Union[int, List[int]], lambda_: float, 
                       cumulative: bool = False,
                       lower_tail: bool = True) -> Union[float, np.ndarray]:
    """Calculate Poisson probability
    
    Parameters:
    -----------
    k : int or list of int
        Number of events
    lambda_ : float
        Mean number of events in the interval
    cumulative : bool, optional
        If True, calculate cumulative probability. Default is False.
    lower_tail : bool, optional
        If True, calculate P(X ≤ k) for cumulative; otherwise P(X > k). Default is True.
        
    Returns:
    --------
    float or numpy.ndarray : Probability or probabilities
    """
    if cumulative:
        if lower_tail:
            return stats.poisson.cdf(k, lambda_)
        else:
            return stats.poisson.sf(k, lambda_)
    else:
        return stats.poisson.pmf(k, lambda_)


def hypergeometric_probability(k: Union[int, List[int]], M: int, n: int, N: int,
                             cumulative: bool = False,
                             lower_tail: bool = True) -> Union[float, np.ndarray]:
    """Calculate hypergeometric probability
    
    Parameters:
    -----------
    k : int or list of int
        Number of successes
    M : int
        Total number of objects in the population
    n : int
        Number of objects with the desired feature
    N : int
        Number of objects drawn
    cumulative : bool, optional
        If True, calculate cumulative probability. Default is False.
    lower_tail : bool, optional
        If True, calculate P(X ≤ k) for cumulative; otherwise P(X > k). Default is True.
        
    Returns:
    --------
    float or numpy.ndarray : Probability or probabilities
    """
    if cumulative:
        if lower_tail:
            return stats.hypergeom.cdf(k, M, n, N)
        else:
            return stats.hypergeom.sf(k, M, n, N)
    else:
        return stats.hypergeom.pmf(k, M, n, N)


def negative_binomial_probability(k: Union[int, List[int]], n: int, p: float,
                                cumulative: bool = False,
                                lower_tail: bool = True) -> Union[float, np.ndarray]:
    """Calculate negative binomial probability
    
    Parameters:
    -----------
    k : int or list of int
        Number of failures before the n-th success
    n : int
        Number of successes
    p : float
        Probability of success in a single trial
    cumulative : bool, optional
        If True, calculate cumulative probability. Default is False.
    lower_tail : bool, optional
        If True, calculate P(X ≤ k) for cumulative; otherwise P(X > k). Default is True.
        
    Returns:
    --------
    float or numpy.ndarray : Probability or probabilities
    """
    if cumulative:
        if lower_tail:
            return stats.nbinom.cdf(k, n, p)
        else:
            return stats.nbinom.sf(k, n, p)
    else:
        return stats.nbinom.pmf(k, n, p)


def geometric_probability(k: Union[int, List[int]], p: float,
                         cumulative: bool = False,
                         lower_tail: bool = True) -> Union[float, np.ndarray]:
    """Calculate geometric probability
    
    Parameters:
    -----------
    k : int or list of int
        Number of failures before the first success
    p : float
        Probability of success in a single trial
    cumulative : bool, optional
        If True, calculate cumulative probability. Default is False.
    lower_tail : bool, optional
        If True, calculate P(X ≤ k) for cumulative; otherwise P(X > k). Default is True.
        
    Returns:
    --------
    float or numpy.ndarray : Probability or probabilities
    """
    if cumulative:
        if lower_tail:
            return stats.geom.cdf(k, p)
        else:
            return stats.geom.sf(k, p)
    else:
        return stats.geom.pmf(k, p)


def normal_probability(x: Union[float, List[float]], mean: float = 0, std: float = 1,
                      cumulative: bool = False,
                      lower_tail: bool = True) -> Union[float, np.ndarray]:
    """Calculate normal probability
    
    Parameters:
    -----------
    x : float or list of float
        Value(s) at which to evaluate the probability
    mean : float, optional
        Mean of the normal distribution. Default is 0.
    std : float, optional
        Standard deviation of the normal distribution. Default is 1.
    cumulative : bool, optional
        If True, calculate cumulative probability. Default is False.
    lower_tail : bool, optional
        If True, calculate P(X ≤ x) for cumulative; otherwise P(X > x). Default is True.
        
    Returns:
    --------
    float or numpy.ndarray : Probability or probabilities
    """
    if cumulative:
        if lower_tail:
            return stats.norm.cdf(x, loc=mean, scale=std)
        else:
            return stats.norm.sf(x, loc=mean, scale=std)
    else:
        return stats.norm.pdf(x, loc=mean, scale=std)


def poisson_interval(lambda_: float, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate confidence interval for Poisson parameter lambda
    
    Parameters:
    -----------
    lambda_ : float
        Observed value of lambda (mean number of events)
    confidence : float, optional
        Confidence level. Default is 0.95 (95% confidence).
        
    Returns:
    --------
    tuple : (lower, upper) bounds of the confidence interval
    """
    alpha = 1 - confidence
    if lambda_ > 0:
        lower = stats.chi2.ppf(alpha/2, 2*lambda_) / 2
    else:
        lower = 0
    upper = stats.chi2.ppf(1-alpha/2, 2*(lambda_+1)) / 2
    
    return (lower, upper)


def binomial_interval(k: int, n: int, method: str = 'wilson', confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate confidence interval for binomial proportion
    
    Parameters:
    -----------
    k : int
        Number of successes
    n : int
        Number of trials
    method : str, optional
        Method for interval calculation: 'wilson', 'normal', 'agresti-coull', 'jeffreys', or 'clopper-pearson'.
        Default is 'wilson'.
    confidence : float, optional
        Confidence level. Default is 0.95 (95% confidence).
        
    Returns:
    --------
    tuple : (lower, upper) bounds of the confidence interval
    """
    from statsmodels.stats.proportion import proportion_confint
    
    p_hat = k / n
    
    valid_methods = ['wilson', 'normal', 'agresti-coull', 'jeffreys', 'clopper-pearson']
    if method not in valid_methods:
        raise ValueError(f"Unknown method: {method}. Choose from {valid_methods}")
    
    lower, upper = proportion_confint(k, n, alpha=(1-confidence), method=method)
    
    return (lower, upper)


def plot_binomial_distribution(n: int, p: float, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Plot binomial probability mass function
    
    Parameters:
    -----------
    n : int
        Number of trials
    p : float
        Probability of success in a single trial
    figsize : tuple, optional
        Figure size. Default is (10, 6).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    x = np.arange(0, n + 1)
    pmf = stats.binom.pmf(x, n, p)
    cdf = stats.binom.cdf(x, n, p)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    ax1.bar(x, pmf, alpha=0.7, label=f'n = {n}, p = {p}')
    ax1.set_xlabel('Number of Successes (k)')
    ax1.set_ylabel('Probability')
    ax1.set_title('Binomial Probability Mass Function')
    ax1.grid(alpha=0.3)
    ax1.legend()
    ax2.step(np.append(x, x[-1]), np.append(cdf, cdf[-1]), where='post', 
            label=f'n = {n}, p = {p}')
    ax2.set_xlabel('Number of Successes (k)')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Binomial Cumulative Distribution Function')
    ax2.grid(alpha=0.3)
    ax2.legend()
    mean = n * p
    var = n * p * (1 - p)
    std = np.sqrt(var)
    fig.text(0.5, 0.01, 
            f"Mean: {mean:.2f}\nStandard Deviation: {std:.2f}\nVariance: {var:.2f}",
            ha='center', va='bottom',
            bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.5"))
    
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    return fig


def plot_poisson_distribution(lambda_: float, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Plot Poisson probability mass function
    
    Parameters:
    -----------
    lambda_ : float
        Mean number of events
    figsize : tuple, optional
        Figure size. Default is (10, 6).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    max_x = max(20, int(lambda_ + 4 * np.sqrt(lambda_)))
    x = np.arange(0, max_x + 1)
    pmf = stats.poisson.pmf(x, lambda_)
    cdf = stats.poisson.cdf(x, lambda_)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    ax1.bar(x, pmf, alpha=0.7, label=f'λ = {lambda_}')
    ax1.set_xlabel('Number of Events (k)')
    ax1.set_ylabel('Probability')
    ax1.set_title('Poisson Probability Mass Function')
    ax1.grid(alpha=0.3)
    ax1.legend()
    ax2.step(np.append(x, x[-1]), np.append(cdf, cdf[-1]), where='post', 
            label=f'λ = {lambda_}')
    ax2.set_xlabel('Number of Events (k)')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Poisson Cumulative Distribution Function')
    ax2.grid(alpha=0.3)
    ax2.legend()
    mean = lambda_
    var = lambda_
    std = np.sqrt(var)
    ci = poisson_interval(lambda_)
    fig.text(0.5, 0.01, 
            f"Mean: {mean:.2f}\nStandard Deviation: {std:.2f}\nVariance: {var:.2f}\n" +
            f"95% CI for λ: ({ci[0]:.2f}, {ci[1]:.2f})",
            ha='center', va='bottom',
            bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.5"))
    
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    return fig


def calculate_waiting_time(arrival_rate: float, n_arrivals: int = 1) -> Dict[str, Any]:
    """Calculate waiting time statistics for Poisson arrivals
    
    Parameters:
    -----------
    arrival_rate : float
        Rate of arrivals (per unit time)
    n_arrivals : int, optional
        Number of arrivals to wait for. Default is 1.
        
    Returns:
    --------
    dict with waiting time statistics
    """
    mean = n_arrivals / arrival_rate
    var = n_arrivals / (arrival_rate ** 2)
    std = np.sqrt(var)
    lower = stats.gamma.ppf(0.025, n_arrivals, scale=1/arrival_rate)
    upper = stats.gamma.ppf(0.975, n_arrivals, scale=1/arrival_rate)
    def prob_less_than(time: float) -> float:
        return stats.gamma.cdf(time, n_arrivals, scale=1/arrival_rate)
    def prob_more_than(time: float) -> float:
        return stats.gamma.sf(time, n_arrivals, scale=1/arrival_rate)
    
    return {
        'mean': mean,
        'variance': var,
        'std': std,
        'ci_95': (lower, upper),
        'prob_less_than': prob_less_than,
        'prob_more_than': prob_more_than
    }


def plot_waiting_time(arrival_rate: float, n_arrivals: int = 1,
                     time_range: Optional[Tuple[float, float]] = None,
                     figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Plot waiting time distribution for Poisson arrivals
    
    Parameters:
    -----------
    arrival_rate : float
        Rate of arrivals (per unit time)
    n_arrivals : int, optional
        Number of arrivals to wait for. Default is 1.
    time_range : tuple, optional
        Range of time to plot. Default is None (auto-calculated).
    figsize : tuple, optional
        Figure size. Default is (10, 6).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    stats_dict = calculate_waiting_time(arrival_rate, n_arrivals)
    if time_range is None:
        mean = stats_dict['mean']
        std = stats_dict['std']
        time_range = (0, mean + 3 * std)
    t = np.linspace(time_range[0], time_range[1], 1000)
    if n_arrivals == 1:
        pdf = stats.expon.pdf(t, scale=1/arrival_rate)
        cdf = stats.expon.cdf(t, scale=1/arrival_rate)
    else:
        pdf = stats.gamma.pdf(t, n_arrivals, scale=1/arrival_rate)
        cdf = stats.gamma.cdf(t, n_arrivals, scale=1/arrival_rate)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    ax1.plot(t, pdf, label=f'λ = {arrival_rate}, n = {n_arrivals}')
    ax1.set_xlabel('Waiting Time')
    ax1.set_ylabel('Probability Density')
    ax1.set_title('Waiting Time Probability Density Function')
    ax1.grid(alpha=0.3)
    ax1.legend()
    mean = stats_dict['mean']
    median = stats.gamma.ppf(0.5, n_arrivals, scale=1/arrival_rate)
    
    ax1.axvline(mean, color='red', linestyle='--', label=f'Mean = {mean:.2f}')
    ax1.axvline(median, color='green', linestyle='--', label=f'Median = {median:.2f}')
    ax1.legend()
    ax2.plot(t, cdf)
    ax2.set_xlabel('Waiting Time')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Waiting Time Cumulative Distribution Function')
    ax2.grid(alpha=0.3)
    ci = stats_dict['ci_95']
    ax2.axvline(ci[0], color='red', linestyle=':', label=f'95% CI: ({ci[0]:.2f}, {ci[1]:.2f})')
    ax2.axvline(ci[1], color='red', linestyle=':')
    ax2.axhline(0.95, color='blue', linestyle=':', alpha=0.5)
    ax2.legend()
    fig.text(0.5, 0.01, 
            f"Mean: {mean:.2f}\nMedian: {median:.2f}\n" +
            f"Std. Dev.: {stats_dict['std']:.2f}\n" +
            f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f})",
            ha='center', va='bottom',
            bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.5"))
    
    fig.tight_layout(rect=[0, 0.1, 1, 0.95])
    if n_arrivals == 1:
        title = f"Exponential Waiting Time Distribution (λ = {arrival_rate})"
    else:
        title = f"Gamma Waiting Time Distribution for {n_arrivals} Arrivals (λ = {arrival_rate})"
    
    fig.suptitle(title, fontsize=14)
    
    return fig


def calculate_z_score(x: float, mean: float, std: float) -> float:
    """Calculate z-score (number of standard deviations from the mean)
    
    Parameters:
    -----------
    x : float
        Value
    mean : float
        Mean of the distribution
    std : float
        Standard deviation of the distribution
        
    Returns:
    --------
    float : z-score
    """
    return (x - mean) / std


def z_to_p(z: float, two_tailed: bool = True) -> float:
    """Convert z-score to p-value
    
    Parameters:
    -----------
    z : float
        Z-score
    two_tailed : bool, optional
        If True, calculate two-tailed p-value. Default is True.
        
    Returns:
    --------
    float : p-value
    """
    if two_tailed:
        return 2 * (1 - stats.norm.cdf(abs(z)))
    else:
        return stats.norm.sf(z) if z > 0 else stats.norm.cdf(z)


def p_to_z(p: float, two_tailed: bool = True) -> float:
    """Convert p-value to z-score
    
    Parameters:
    -----------
    p : float
        P-value
    two_tailed : bool, optional
        If True, calculate z-score for two-tailed p-value. Default is True.
        
    Returns:
    --------
    float : z-score
    """
    if two_tailed:
        return stats.norm.ppf(1 - p/2)
    else:
        return stats.norm.ppf(1 - p)


def plot_normal_distribution(mean: float = 0, std: float = 1, x_range: Optional[Tuple[float, float]] = None,
                           shade_area: Optional[Tuple[float, float]] = None, 
                           figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Plot normal probability density function with optional shaded area
    
    Parameters:
    -----------
    mean : float, optional
        Mean of the normal distribution. Default is 0.
    std : float, optional
        Standard deviation of the normal distribution. Default is 1.
    x_range : tuple, optional
        Range of x values to plot. Default is None (auto-calculated).
    shade_area : tuple, optional
        Range of x values to shade under the curve. Default is None (no shading).
    figsize : tuple, optional
        Figure size. Default is (10, 6).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    if x_range is None:
        x_range = (mean - 4*std, mean + 4*std)
    x = np.linspace(x_range[0], x_range[1], 1000)
    pdf = stats.norm.pdf(x, loc=mean, scale=std)
    cdf = stats.norm.cdf(x, loc=mean, scale=std)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    ax1.plot(x, pdf, 'b-', linewidth=2)
    ax1.set_xlabel('x')
    ax1.set_ylabel('Probability Density')
    ax1.set_title('Normal Probability Density Function')
    if shade_area is not None:
        shade_start = max(shade_area[0], x_range[0])
        shade_end = min(shade_area[1], x_range[1])
        shade_x = np.linspace(shade_start, shade_end, 1000)
        shade_pdf = stats.norm.pdf(shade_x, loc=mean, scale=std)
        ax1.fill_between(shade_x, shade_pdf, alpha=0.3)
        prob = stats.norm.cdf(shade_end, loc=mean, scale=std) - stats.norm.cdf(shade_start, loc=mean, scale=std)
        ax1.text(0.95, 0.95, f"P({shade_start:.2f} < X < {shade_end:.2f}) = {prob:.4f}",
                ha='right', va='top', transform=ax1.transAxes,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2"))
    ax1.axvline(mean, color='r', linestyle='--', label=f'Mean = {mean}')
    ax1.axvline(mean + std, color='g', linestyle=':', label=f'Mean ± σ')
    ax1.axvline(mean - std, color='g', linestyle=':')
    ax1.legend()
    ax2.plot(x, cdf, 'b-', linewidth=2)
    ax2.set_xlabel('x')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Normal Cumulative Distribution Function')
    if shade_area is not None:
        shade_start = max(shade_area[0], x_range[0])
        shade_end = min(shade_area[1], x_range[1])
        ax2.axvline(shade_start, color='r', linestyle=':', alpha=0.5)
        ax2.axvline(shade_end, color='r', linestyle=':', alpha=0.5)
        p_start = stats.norm.cdf(shade_start, loc=mean, scale=std)
        p_end = stats.norm.cdf(shade_end, loc=mean, scale=std)
        
        ax2.axhline(p_start, color='r', linestyle=':', alpha=0.5)
        ax2.axhline(p_end, color='r', linestyle=':', alpha=0.5)
        ax2.text(0.95, 0.5, f"P({shade_start:.2f} < X < {shade_end:.2f}) = {prob:.4f}",
                ha='right', va='center', transform=ax2.transAxes,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2"))
    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)
    percentiles = [
        ('1st', 0.01), ('5th', 0.05), ('10th', 0.1),
        ('25th', 0.25), ('50th', 0.5), ('75th', 0.75),
        ('90th', 0.9), ('95th', 0.95), ('99th', 0.99)
    ]
    
    percentile_values = [f"{name} percentile: {stats.norm.ppf(p, loc=mean, scale=std):.2f}" 
                        for name, p in percentiles]
    percentile_text = "\n".join(percentile_values)
    fig.text(0.5, 0.01, 
            f"Mean: {mean}\nStd Dev: {std}\nVariance: {std**2}\n\n{percentile_text}",
            ha='center', va='bottom',
            bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.5"))
    
    fig.tight_layout(rect=[0, 0.2, 1, 0.95])
    fig.suptitle(f"Normal Distribution (μ = {mean}, σ = {std})", fontsize=14)
    
    return fig