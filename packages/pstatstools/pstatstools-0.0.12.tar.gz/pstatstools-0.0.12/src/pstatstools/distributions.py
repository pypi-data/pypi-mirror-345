import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from scipy.special import factorial
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from abc import ABC, abstractmethod

def distribution(dist_type: str, *args, **kwargs) -> 'Distribution':
    """Factory function to create a Distribution object
    
    Parameters:
    dist_type : str
        Type of distribution (normal, t, chi2, f, etc.)
    *args, **kwargs : 
        Parameters for the distribution
    
    Returns:
    Distribution object of the specified type
    """
    dist_map = {
        'normal': NormalDistribution,
        'gaussian': NormalDistribution,
        'norm': NormalDistribution,
        't': TDistribution,
        'student': TDistribution,
        'chi2': Chi2Distribution,
        'chisquare': Chi2Distribution,
        'chi-square': Chi2Distribution,
        'f': FDistribution,
        'exp': ExponentialDistribution,
        'exponential': ExponentialDistribution,
        'poisson': PoissonDistribution,
        'binomial': BinomialDistribution,
        'binom': BinomialDistribution,
        'uniform': UniformDistribution,
        'unif': UniformDistribution,
        'beta': BetaDistribution,
        'gamma': GammaDistribution,
        'lognormal': LogNormalDistribution,
        'lognorm': LogNormalDistribution,
        'geometric': GeometricDistribution,
        'geom': GeometricDistribution,
        'weibull': WeibullDistribution,
        'cauchy': CauchyDistribution,
        'nbinom': NegativeBinomialDistribution,
        'negbinom': NegativeBinomialDistribution,
        'negative_binomial': NegativeBinomialDistribution,
        'hypergeometric': HypergeometricDistribution,
        'hypergeom': HypergeometricDistribution
    }
    
    dist_type_lower = dist_type.lower()
    if dist_type_lower not in dist_map:
        available_types = set(distribution_class.__name__.replace('Distribution', '') 
                              for distribution_class in set(dist_map.values()))
        raise ValueError(f"Unknown distribution type: {dist_type}. " 
                         f"Available types: {', '.join(sorted(available_types))}")
        
    return dist_map[dist_type_lower](*args, **kwargs)


class Distribution(ABC):
    """Base class for probability distributions"""
    
    def __init__(self):
        """Initialize a distribution object"""
        self.dist = None
        self.params: Dict[str, Any] = {}
        self.continuous: bool = True
        self.name: str = "Generic Distribution"
        
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Probability density function (PDF)
        
        For continuous distributions, this returns the probability density at point x.
        For discrete distributions, this returns the probability mass at point x.
        """
        if self.continuous:
            return self.dist.pdf(x)
        else:
            return self.dist.pmf(x)
    
    def pmf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Probability mass function (PMF) for discrete distributions"""
        if not self.continuous:
            return self.dist.pmf(x)
        else:
            raise ValueError(f"{self.name} is a continuous distribution and does not have a PMF.")
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Cumulative distribution function (CDF)"""
        return self.dist.cdf(x)
    
    def sf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Survival function (1 - CDF)"""
        return self.dist.sf(x)
    
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Percent point function (inverse of CDF)
        
        Parameters:
        q : float or array-like
            Probability between 0 and 1
            
        Returns:
        x value at which CDF(x) = q
        """
        return self.dist.ppf(q)
    
    def isf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Inverse survival function (inverse of SF)"""
        return self.dist.isf(q)
    
    def mean(self) -> float:
        """Mean of the distribution"""
        return self.dist.mean()
    
    def var(self) -> float:
        """Variance of the distribution"""
        return self.dist.var()
    
    def std(self) -> float:
        """Standard deviation of the distribution"""
        return self.dist.std()
    
    def median(self) -> float:
        """Median of the distribution"""
        return self.dist.median()
    
    def mode(self) -> float:
        """Mode of the distribution"""
        if hasattr(self.dist, 'mode'):
            return self.dist.mode()
        else:
            raise NotImplementedError(f"Mode calculation not implemented for {self.name}")
    
    def moment(self, n: int) -> float:
        """n-th central moment of the distribution"""
        return self.dist.moment(n)
    
    def skewness(self) -> float:
        """Skewness of the distribution"""
        return self.dist.stats(moments='s')
    
    def kurtosis(self) -> float:
        """Kurtosis of the distribution"""
        return self.dist.stats(moments='k')
    
    def stats(self, moments: str = 'mvsk') -> Union[float, Tuple[float, ...]]:
        """Return mean, variance, skewness, and/or kurtosis
        
        Parameters:
        moments : str, optional
            String composed of letters 'm', 'v', 's', and/or 'k'.
            Default is 'mvsk' for all four moments.
        """
        return self.dist.stats(moments=moments)
    
    def entropy(self) -> float:
        """Differential entropy of the distribution in nats"""
        return self.dist.entropy()
    
    def interval(self, alpha: float) -> Tuple[float, float]:
        """Confidence interval with equal areas in both tails
        
        Parameters:
        alpha : float
            Confidence level, i.e. 0.95 for 95% confidence interval
            
        Returns:
        (lower, upper) bounds of the interval
        """
        return self.dist.interval(alpha)
    
    def random(self, size: Union[int, Tuple[int, ...]] = 1, random_state: Optional[Union[int, np.random.RandomState]] = None) -> Union[float, np.ndarray]:
        """Generate random samples from the distribution
        
        Parameters:
        size : int or tuple, optional
            Output shape of samples. Default is 1.
            
        Returns:
        Random samples from the distribution
        """
        return self.dist.rvs(size=size, random_state=random_state)
    
    def rvs(self, size: Union[int, Tuple[int, ...]] = 1, 
            random_state: Optional[Union[int, np.random.RandomState]] = None) -> Union[float, np.ndarray]:
        """Generate random variates from the distribution (alias for random)"""
        return self.dist.rvs(size=size, random_state=random_state)
    
    def bootstrap_statistic(self, n: int, statistic: Callable = np.median,
                                  n_samples: int = 10000, 
                                  conf_level: float = 0.99,
                                  random_state: Optional[Union[int, np.random.RandomState]] = None) -> Tuple[float, float]:
        """Perform parametric bootstrap for any statistic.

        Parameters:
        -----------
        n : int
            Sample size for each bootstrap sample
        statistic : callable, optional
            Function to compute the statistic (e.g., np.median, np.mean, np.std). Default is np.median.
        n_samples : int, optional
            Number of bootstrap samples. Default is 10000.
        conf_level : float, optional
            Confidence level (e.g., 0.99 for 99%). Default is 0.99.
        random_state : int or RandomState, optional
            Random state for reproducibility. Default is None.

        Returns:
        --------
        Tuple[float, float]
            (lower_bound, upper_bound) of the confidence interval

        Example:
        --------
        >>> dist = distribution('normal', mu=4.03, sigma=0.49)
        >>> # Confidence interval for median
        >>> lower, upper = dist.parametric_bootstrap_statistic(n=30, statistic=np.median)
        >>> # Confidence interval for standard deviation
        >>> lower, upper = dist.parametric_bootstrap_statistic(n=30, statistic=lambda x: np.std(x, ddof=1))
        """
        samples = self.random(size=(n_samples, n), random_state=random_state)
        bootstrap_stats = np.array([statistic(sample) for sample in samples])

        alpha = 1 - conf_level
        lower_bound = np.percentile(bootstrap_stats, alpha/2 * 100)
        upper_bound = np.percentile(bootstrap_stats, (1 - alpha/2) * 100)
    
        return (lower_bound, upper_bound)
    
    def fit(self, data: np.ndarray) -> Tuple:
        """Fit the distribution to data and return fitted parameters
        
        Parameters:
        data : array-like
            Data to fit the distribution to
            
        Returns:
        Fitted distribution parameters
        """
        if hasattr(self.dist, 'fit'):
            return self.dist.fit(data)
        else:
            raise NotImplementedError(f"Fitting not implemented for {self.name}")
    
    def logpdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log of the probability density function"""
        if self.continuous:
            return self.dist.logpdf(x)
        else:
            return self.dist.logpmf(x)
    
    def logpmf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log of the probability mass function"""
        if not self.continuous:
            return self.dist.logpmf(x)
        else:
            raise ValueError(f"{self.name} is a continuous distribution and does not have a PMF.")
    
    def logcdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log of the cumulative distribution function"""
        return self.dist.logcdf(x)
    
    def logsf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log of the survival function"""
        return self.dist.logsf(x)
    
    @abstractmethod
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting based on distribution parameters"""
        pass
    
    #-----------------------------------------------------------------
    # Visualization Methods
    #-----------------------------------------------------------------
    
    def plot_pdf(self, x_range: Optional[Tuple[float, float]] = None, 
                num_points: int = 1000, ax: Optional[plt.Axes] = None, 
                **kwargs) -> plt.Axes:
        """Plot the probability density function (PDF) or probability mass function (PMF)
        
        Parameters:
        x_range : tuple, optional
            Range (min, max) for x-axis. Default is based on distribution parameters.
        num_points : int, optional
            Number of points to plot for continuous distributions. Default is 1000.
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates a new figure.
        **kwargs :
            Additional keyword arguments to pass to the plot function.
            
        Returns:
        matplotlib.axes.Axes
        """
        ax = self._setup_plot_axes(ax, kwargs.pop('figsize', (8, 6)))
        x_range = self._determine_x_range(x_range)
        
        title = kwargs.pop('title', f"{self.name} {'PDF' if self.continuous else 'PMF'}")
        xlabel = kwargs.pop('xlabel', 'x')
        ylabel = kwargs.pop('ylabel', 'Density' if self.continuous else 'Probability')
        
        self._plot_distribution_function(ax, x_range, num_points, 'pdf', **kwargs)
            
        self._set_plot_aesthetics(ax, title, xlabel, ylabel)
        
        return ax
    
    def plot_cdf(self, x_range: Optional[Tuple[float, float]] = None, 
                num_points: int = 1000, ax: Optional[plt.Axes] = None, 
                **kwargs) -> plt.Axes:
        """Plot the cumulative distribution function (CDF)
        
        Parameters:
        x_range : tuple, optional
            Range (min, max) for x-axis. Default is based on distribution parameters.
        num_points : int, optional
            Number of points to plot. Default is 1000.
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates a new figure.
        **kwargs :
            Additional keyword arguments to pass to the plot function.
            
        Returns:
        matplotlib.axes.Axes
        """
        ax = self._setup_plot_axes(ax, kwargs.pop('figsize', (8, 6)))
        x_range = self._determine_x_range(x_range)
        
        title = kwargs.pop('title', f"{self.name} CDF")
        xlabel = kwargs.pop('xlabel', 'x')
        ylabel = kwargs.pop('ylabel', 'Probability')
        
        self._plot_distribution_function(ax, x_range, num_points, 'cdf', **kwargs)
            
        self._set_plot_aesthetics(ax, title, xlabel, ylabel)
        
        return ax
    
    def plot_both(self, x_range: Optional[Tuple[float, float]] = None, 
                 num_points: int = 1000, figsize: Tuple[int, int] = (10, 5), 
                 **kwargs) -> plt.Figure:
        """Plot both PDF/PMF and CDF side by side
        
        Parameters:
        x_range : tuple, optional
            Range (min, max) for x-axis. Default is based on distribution parameters.
        num_points : int, optional
            Number of points to plot. Default is 1000.
        figsize : tuple, optional
            Figure size. Default is (10, 5).
        **kwargs :
            Additional keyword arguments to pass to the plot functions.
            
        Returns:
        matplotlib.figure.Figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        self.plot_pdf(x_range, num_points, ax=ax1, **kwargs)
        self.plot_cdf(x_range, num_points, ax=ax2, **kwargs)
        
        plt.tight_layout()
        return fig
    
    def _setup_plot_axes(self, ax: Optional[plt.Axes], 
                         figsize: Tuple[int, int]) -> plt.Axes:
        """Set up axes for plotting"""
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)
        return ax
    
    def _determine_x_range(self, x_range: Optional[Tuple[float, float]]) -> Tuple[float, float]:
        """Determine the x-range for plotting"""
        if x_range is None:
            if self.continuous:
                x_range = self._get_x_range()
            else:
                # For discrete distributions, create a reasonable range for the PMF
                if hasattr(self, '_get_x_range'):
                    x_range = self._get_x_range()
                else:
                    # Try a reasonable default
                    mean = self.mean()
                    std = self.std()
                    lower = max(0, int(mean - 3 * std)) if std < float('inf') else 0
                    upper = int(mean + 3 * std) if std < float('inf') else 20
                    x_range = (lower, upper)
        return x_range
    
    def _plot_distribution_function(self, ax: plt.Axes, 
                                   x_range: Tuple[float, float], 
                                   num_points: int, 
                                   func_type: str, 
                                   **kwargs) -> None:
        """Plot a specific distribution function (PDF, PMF, CDF)"""
        if self.continuous:
            x = np.linspace(x_range[0], x_range[1], num_points)
            y = getattr(self, func_type)(x)
            if func_type == 'cdf':
                ax.plot(x, y, **kwargs)
            else:  # pdf
                ax.plot(x, y, **kwargs)
        else:
            x = np.arange(x_range[0], x_range[1] + 1)
            y = getattr(self, func_type)(x)
            if func_type == 'cdf':
                # For discrete, we use a step function for CDF
                ax.step(np.append(x, x[-1]), np.append(y, y[-1]), where='post', **kwargs)
            else:  # pmf
                ax.bar(x, y, width=0.8, alpha=0.7, **kwargs)
    
    def _set_plot_aesthetics(self, ax: plt.Axes, title: str, 
                            xlabel: str, ylabel: str) -> None:
        """Set aesthetics for the plot"""
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    
    #-----------------------------------------------------------------
    # Utility Methods
    #-----------------------------------------------------------------
    
    def describe(self, print_format: bool = True) -> Dict[str, Any]:
        """Print a summary of the distribution properties
        
        Parameters:
        print_format : bool, optional
            Whether to print the summary. Default is True.
            
        Returns:
        dict with distribution properties
        """
        try:
            properties = self._calculate_properties()
            
            if print_format:
                self._print_properties(properties)
            
            return properties
        
        except Exception as e:
            print(f"Could not calculate all properties: {e}")
            return self.params
    
    def _calculate_properties(self) -> Dict[str, Any]:
        """Calculate statistical properties for the distribution"""
        return {
            'name': self.name,
            'type': 'Continuous' if self.continuous else 'Discrete',
            'parameters': self.params,
            'mean': self.mean(),
            'variance': self.var(),
            'std': self.std(),
            'median': self.median(),
            'skewness': self.skewness(),
            'kurtosis': self.kurtosis(),
            '95% interval': self.interval(0.95)
        }
    
    def _print_properties(self, properties: Dict[str, Any]) -> None:
        """Print formatted properties"""
        print(f"=== {properties['name']} Distribution Summary ===")
        print(f"Type: {properties['type']}")
        
        print("\nParameters:")
        for param, value in properties['parameters'].items():
            print(f"  {param}: {value}")
        
        print("\nProperties:")
        for prop, value in properties.items():
            if prop not in ['name', 'type', 'parameters']:
                print(f"  {prop}: {value}")
    
    def sf_to_p_value(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert test statistic to p-value using the survival function
        
        Parameters:
        x : float or array-like
            Test statistic value
            
        Returns:
        p-value
        """
        return self.sf(x)
    
    def compare_with_data(self, data: np.ndarray, bins: Union[int, str] = 'auto', 
                         figsize: Tuple[int, int] = (10, 6), **kwargs) -> plt.Figure:
        """Compare the theoretical distribution with observed data
        
        Parameters:
        data : array-like
            Observed data to compare with
        bins : int or str, optional
            Number of bins for histogram. Default is 'auto'.
        figsize : tuple, optional
            Figure size. Default is (10, 6).
        **kwargs :
            Additional keyword arguments to pass to plotting functions.
            
        Returns:
        matplotlib.figure.Figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot histogram of data
        counts, bin_edges, _ = ax.hist(
            data, 
            bins=bins, 
            density=True, 
            alpha=0.5, 
            label='Observed Data',
            color=kwargs.pop('hist_color', 'steelblue')
        )
        
        self._overlay_theoretical_distribution(ax, data, bin_edges, **kwargs)
        goodness_text = self._calculate_goodness_of_fit(data)
        
        self._add_goodness_of_fit_textbox(ax, goodness_text)
        self._set_compare_plot_aesthetics(ax)
        
        return fig
    
    def _overlay_theoretical_distribution(self, ax: plt.Axes, data: np.ndarray, 
                                         bin_edges: np.ndarray, **kwargs) -> None:
        """Overlay theoretical distribution on histogram"""
        # If continuous, overlay PDF
        if self.continuous:
            x = np.linspace(bin_edges[0], bin_edges[-1], 1000)
            y = self.pdf(x)
            ax.plot(x, y, 'r-', lw=2, label=f'{self.name} PDF', 
                   color=kwargs.pop('pdf_color', 'crimson'))
        # For discrete, overlay PMF as bars
        else:
            x_range = (int(min(data)), int(max(data)))
            x = np.arange(x_range[0], x_range[1] + 1)
            y = self.pmf(x)
            ax.bar(x, y, alpha=0.7, color='crimson', width=0.4, label=f'{self.name} PMF')
    
    def _calculate_goodness_of_fit(self, data: np.ndarray) -> str:
        """Calculate goodness-of-fit test results"""
        if self.continuous:
            return self._calculate_ks_test(data)
        else:
            return self._calculate_chi_square_test(data)
    
    def _calculate_ks_test(self, data: np.ndarray) -> str:
        """Calculate Kolmogorov-Smirnov test for continuous distributions"""
        try:
            ks_stat, ks_pval = stats.kstest(data, self.cdf)
            return f"KS Test: p-value = {ks_pval:.4f}"
        except Exception:
            return "Could not perform KS test"
    
    def _calculate_chi_square_test(self, data: np.ndarray) -> str:
        """Calculate Chi-square test for discrete distributions"""
        try:
            # For discrete distributions, we can use chi-squared test
            observed = pd.Series(data).value_counts().sort_index()
            x_values = observed.index.values
            expected = self.pmf(x_values) * len(data)
            
            # Only use bins with expected values > 5
            valid_bins = expected >= 5
            if sum(valid_bins) > 5:  # Need at least 5 valid bins
                chi2_stat, chi2_pval = stats.chisquare(
                    observed[valid_bins], 
                    expected[valid_bins]
                )
                return f"Chi-Square Test: p-value = {chi2_pval:.4f}"
            else:
                return "Too few samples for Chi-Square test"
        except Exception:
            return "Could not perform Chi-Square test"
    
    def _add_goodness_of_fit_textbox(self, ax: plt.Axes, goodness_text: str) -> None:
        """Add goodness-of-fit textbox to plot"""
        ax.text(
            0.95, 0.95, 
            goodness_text,
            transform=ax.transAxes, 
            verticalalignment='top', 
            horizontalalignment='right',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.3}
        )
    
    def _set_compare_plot_aesthetics(self, ax: plt.Axes) -> None:
        """Set aesthetics for the comparison plot"""
        ax.set_title(f"Comparison of Data with {self.name} Distribution")
        ax.set_xlabel('Value')
        ax.set_ylabel('Density/Probability')
        ax.legend()
        ax.grid(alpha=0.3)
    
    def qq_plot(self, data: np.ndarray, figsize: Tuple[int, int] = (8, 8), 
               **kwargs) -> plt.Figure:
        """Create a quantile-quantile (Q-Q) plot to compare distribution with data
        
        Parameters:
        data : array-like
            Observed data to compare with
        figsize : tuple, optional
            Figure size. Default is (8, 8).
        **kwargs :
            Additional keyword arguments to pass to plotting functions.
            
        Returns:
        matplotlib.figure.Figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Sort the observed data
        sorted_data = np.sort(data)
        n = len(sorted_data)
        
        # Calculate theoretical quantiles
        p = np.arange(1, n + 1) / (n + 1)  # plotting positions
        theoretical_quantiles = self.ppf(p)
        
        # Create Q-Q plot
        ax.scatter(theoretical_quantiles, sorted_data, **kwargs)
        
        # Add a reference line
        min_val = min(min(theoretical_quantiles), min(sorted_data))
        max_val = max(max(theoretical_quantiles), max(sorted_data))
        ax.plot([min_val, max_val], [min_val, max_val], 'r-', lw=2)
        
        ax.set_title(f"Q-Q Plot: {self.name} vs. Observed Data")
        ax.set_xlabel('Theoretical Quantiles')
        ax.set_ylabel('Sample Quantiles')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def pp_plot(self, data: np.ndarray, figsize: Tuple[int, int] = (8, 8), 
               **kwargs) -> plt.Figure:
        """Create a probability-probability (P-P) plot to compare distribution with data
        
        Parameters:
        data : array-like
            Observed data to compare with
        figsize : tuple, optional
            Figure size. Default is (8, 8).
        **kwargs :
            Additional keyword arguments to pass to plotting functions.
            
        Returns:
        matplotlib.figure.Figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Sort the observed data
        sorted_data = np.sort(data)
        n = len(sorted_data)
        
        # Calculate observed and theoretical probabilities
        p_observed = np.arange(1, n + 1) / n  # empirical CDF
        p_theoretical = self.cdf(sorted_data)
        
        # Create P-P plot
        ax.scatter(p_theoretical, p_observed, **kwargs)
        
        # Add a reference line
        ax.plot([0, 1], [0, 1], 'r-', lw=2)
        
        ax.set_title(f"P-P Plot: {self.name} vs. Observed Data")
        ax.set_xlabel('Theoretical Probability')
        ax.set_ylabel('Empirical Probability')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def __repr__(self) -> str:
        """String representation of the distribution"""
        param_str = ', '.join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.name}({param_str})"


#-----------------------------------------------------------------
# Specific Distribution Classes
#-----------------------------------------------------------------

class NormalDistribution(Distribution):
    """Normal (Gaussian) distribution"""
    
    def __init__(self, mu: float = 0, sigma: float = 1):
        """Initialize a Normal distribution
        
        Parameters:
        mu : float, optional
            Mean of the distribution. Default is 0.
        sigma : float, optional
            Standard deviation of the distribution. Default is 1.
        """
        super().__init__()
        self.dist = stats.norm(loc=mu, scale=sigma)
        self.params = {'mu': mu, 'sigma': sigma}
        self.name = "Normal"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        mu = self.params['mu']
        sigma = self.params['sigma']
        return (mu - 4*sigma, mu + 4*sigma)
    
    def interpret(self, x: float) -> str:
        """Interpret normal distribution value
        
        Parameters:
        x : float
            Value to interpret
            
        Returns:
        str : Interpretation of the normal value
        """
        mu = self.params['mu']
        sigma = self.params['sigma']
        z_score = (x - mu) / sigma
        percentile = self.cdf(x) * 100
        
        result = f"Value x = {x:.4f}\n"
        result += f"Mean (μ) = {mu:.4f}\n"
        result += f"Standard Deviation (σ) = {sigma:.4f}\n"
        result += f"Z-score = {z_score:.4f}\n"
        result += f"Percentile = {percentile:.2f}%\n\n"
        
        result += "INTERPRETATION:\n"
        if abs(z_score) > 3:
            result += f"This value is more than 3 standard deviations from the mean.\n"
            result += f"It is extremely {('high' if z_score > 0 else 'low')} and very rare in the distribution.\n"
        elif abs(z_score) > 2:
            result += f"This value is more than 2 standard deviations from the mean.\n"
            result += f"It is unusually {('high' if z_score > 0 else 'low')} and occurs in less than 5% of cases.\n"
        elif abs(z_score) > 1:
            result += f"This value is more than 1 standard deviation from the mean.\n"
            result += f"It is somewhat {('above' if z_score > 0 else 'below')} average.\n"
        else:
            result += f"This value is within 1 standard deviation of the mean.\n"
            result += f"It is close to average and quite typical in this distribution.\n"
        
        result += f"\nComparison to population:\n"
        result += f"- {percentile:.1f}% of values are less than or equal to this value\n"
        result += f"- {100-percentile:.1f}% of values are greater than this value\n"
        
        return result



class TDistribution(Distribution):
    """Student's t-distribution"""
    
    def __init__(self, df: float, mu: float = 0, sigma: float = 1):
        """Initialize a Student's t-distribution
        
        Parameters:
        df : float
            Degrees of freedom
        mu : float, optional
            Location parameter. Default is 0.
        sigma : float, optional
            Scale parameter. Default is 1.
        """
        super().__init__()
        self.dist = stats.t(df, loc=mu, scale=sigma)
        self.params = {'df': df, 'mu': mu, 'sigma': sigma}
        self.name = "Student's t"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        mu = self.params['mu']
        sigma = self.params['sigma']
        df = self.params['df']
        # For small df, t has heavier tails
        if df <= 2:
            return (mu - 6*sigma, mu + 6*sigma)
        elif df <= 5:
            return (mu - 5*sigma, mu + 5*sigma)
        else:
            return (mu - 4*sigma, mu + 4*sigma)
        
        
    def interpret(self, t_value: float, test_type: str = 'two-sided', alpha: float = 0.05) -> str:
        """Interpret t-distribution value
        
        Parameters:
        t_value : float
            t value to interpret
        test_type : str, optional
            Type of test: 'two-sided', 'greater', or 'less'. Default is 'two-sided'.
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        str : Interpretation of the t value
        """
        df = self.params['df']
        
        result = f"t value: {t_value:.4f}\n"
        result += f"Degrees of freedom: {df}\n"
        
        if test_type == 'two-sided':
            p_value = 2 * min(self.cdf(t_value), self.sf(t_value))
            critical_t = self.ppf(1 - alpha/2)
            result += f"Two-sided p-value: {p_value:.4f}\n"
            result += f"Critical values at α={alpha}: ±{critical_t:.4f}\n\n"
            
            if p_value <= alpha:
                result += f"Reject the null hypothesis at α={alpha}.\n"
                result += "The sample mean is significantly different from the hypothesized value or\n"
                result += "the two sample means are significantly different from each other.\n"
            else:
                result += f"Fail to reject the null hypothesis at α={alpha}.\n"
                result += "The difference is not statistically significant.\n"
                
        elif test_type == 'greater':
            p_value = self.sf(t_value)
            critical_t = self.ppf(1 - alpha)
            result += f"One-sided (greater) p-value: {p_value:.4f}\n"
            result += f"Critical value at α={alpha}: {critical_t:.4f}\n\n"
            
            if p_value <= alpha:
                result += f"Reject the null hypothesis at α={alpha}.\n"
                result += "The sample mean is significantly greater than the hypothesized value or\n"
                result += "the first group mean is significantly greater than the second.\n"
            else:
                result += f"Fail to reject the null hypothesis at α={alpha}.\n"
                result += "The mean is not significantly greater.\n"
                
        elif test_type == 'less':
            p_value = self.cdf(t_value)
            critical_t = self.ppf(alpha)
            result += f"One-sided (less) p-value: {p_value:.4f}\n"
            result += f"Critical value at α={alpha}: {critical_t:.4f}\n\n"
            
            if p_value <= alpha:
                result += f"Reject the null hypothesis at α={alpha}.\n"
                result += "The sample mean is significantly less than the hypothesized value or\n"
                result += "the first group mean is significantly less than the second.\n"
            else:
                result += f"Fail to reject the null hypothesis at α={alpha}.\n"
                result += "The mean is not significantly less.\n"
        
        effect_size = abs(t_value) / np.sqrt(df + 1)
        result += f"\nEffect size (r): {effect_size:.4f}"
        
        if effect_size > 0.5:
            result += " (large effect)"
        elif effect_size > 0.3:
            result += " (medium effect)"
        elif effect_size > 0.1:
            result += " (small effect)"
        else:
            result += " (negligible effect)"
        
        return result


class Chi2Distribution(Distribution):
    """Chi-squared distribution"""
    
    def __init__(self, df: float, loc: float = 0, scale: float = 1):
        """Initialize a Chi-squared distribution
        
        Parameters:
        df : float
            Degrees of freedom
        loc : float, optional
            Location parameter. Default is 0.
        scale : float, optional
            Scale parameter. Default is 1.
        """
        super().__init__()
        self.dist = stats.chi2(df, loc=loc, scale=scale)
        self.params = {'df': df, 'loc': loc, 'scale': scale}
        self.name = "Chi-squared"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        df = self.params['df']
        loc = self.params['loc']
        scale = self.params['scale']
        # Chi-squared has mean = df and var = 2*df
        upper = loc + scale * max(df + 4 * np.sqrt(2 * df), 20)
        return (loc, upper)
    
    def interpret(self, critical_value: float, alpha: float = 0.05) -> str:
        """Interpret chi-square distribution value
        
        Parameters:
        critical_value : float
            Chi-square value to interpret
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        str : Interpretation of the chi-square value
        """
        df = self.params['df']
        p_value = self.sf(critical_value)
        critical_chi2 = self.ppf(1 - alpha)
        
        result = f"Chi-square value: {critical_value:.4f}\n"
        result += f"Degrees of freedom: {df}\n"
        result += f"P-value: {p_value:.4f}\n"
        result += f"Critical value at α={alpha}: {critical_chi2:.4f}\n\n"
        
        if p_value <= alpha:
            result += f"Reject the null hypothesis at α={alpha}.\n"
            result += "The observed value is significantly different from what would be expected under the null hypothesis.\n"
        else:
            result += f"Fail to reject the null hypothesis at α={alpha}.\n"
            result += "The observed value is not significantly different from what would be expected under the null hypothesis.\n"
            
        if critical_value > 3 * df:
            result += "\nNote: The chi-square value is very large compared to its degrees of freedom, indicating a very poor model fit or strong association."
        elif critical_value > 2 * df:
            result += "\nNote: The chi-square value is larger than expected, suggesting poor model fit or strong association."
        
        return result
    
class FDistribution(Distribution):
    """F-distribution"""
    
    def __init__(self, dfn: float, dfd: float, loc: float = 0, scale: float = 1):
        """Initialize an F-distribution
        
        Parameters:
        dfn : float
            Numerator degrees of freedom
        dfd : float
            Denominator degrees of freedom
        loc : float, optional
            Location parameter. Default is 0.
        scale : float, optional
            Scale parameter. Default is 1.
        """
        super().__init__()
        self.dist = stats.f(dfn, dfd, loc=loc, scale=scale)
        self.params = {'dfn': dfn, 'dfd': dfd, 'loc': loc, 'scale': scale}
        self.name = "F"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        dfn = self.params['dfn']
        dfd = self.params['dfd']
        loc = self.params['loc']
        scale = self.params['scale']
        # F-distribution is right-skewed
        if dfd > 2:
            mean = dfd / (dfd - 2)
            if dfd > 4:
                var = (2 * dfd**2 * (dfn + dfd - 2)) / (dfn * (dfd - 2)**2 * (dfd - 4))
                upper = loc + scale * (mean + 4 * np.sqrt(var))
            else:
                upper = loc + scale * 10  # Just use a large value
        else:
            upper = loc + scale * 10
        return (loc, upper)
    
    def interpret(self, f_value: float, alpha: float = 0.05) -> str:
        """Interpret F-distribution value
        
        Parameters:
        f_value : float
            F value to interpret
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        str : Interpretation of the F value
        """
        dfn = self.params['dfn']
        dfd = self.params['dfd']
        p_value = self.sf(f_value)
        critical_f = self.ppf(1 - alpha)
        
        result = f"F value: {f_value:.4f}\n"
        result += f"Numerator degrees of freedom: {dfn}\n"
        result += f"Denominator degrees of freedom: {dfd}\n"
        result += f"P-value: {p_value:.4f}\n"
        result += f"Critical value at α={alpha}: {critical_f:.4f}\n\n"
        
        if p_value <= alpha:
            result += f"Reject the null hypothesis at α={alpha}.\n"
            result += "The variance ratio is significantly different from what would be expected under the null hypothesis.\n"
            result += "This suggests significant differences between group variances or regression model effects.\n"
        else:
            result += f"Fail to reject the null hypothesis at α={alpha}.\n"
            result += "The variance ratio is not significantly different from what would be expected under the null hypothesis.\n"
            result += "This suggests no significant differences between group variances or no significant regression model.\n"
            
        # F-ratio interpretation
        if f_value > 5:
            result += "\nNote: The F-ratio is quite large, indicating substantial differences in variances or strong model effects."
        elif f_value > 2:
            result += "\nNote: The F-ratio is moderately large, indicating some differences in variances or moderate model effects."
        elif f_value < 0.5:
            result += "\nNote: The F-ratio is small, suggesting minimal differences between variances or weak model effects."
        
        return result



class ExponentialDistribution(Distribution):
    """Exponential distribution"""
    
    def __init__(self, scale: float = 1, loc: float = 0):
        """Initialize an Exponential distribution
        
        Parameters:
        scale : float, optional
            Scale parameter (1/lambda). Default is 1.
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.expon(loc=loc, scale=scale)
        self.params = {'scale': scale, 'loc': loc}
        self.name = "Exponential"
        
    def rate(self) -> float:
        """Return the rate parameter (lambda)"""
        return 1.0 / self.params['scale']
    
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        scale = self.params['scale']
        loc = self.params['loc']
        return (loc, loc + scale * 5)
    
    def interpret(self, x: float) -> str:
        """Interpret exponential distribution value
        
        Parameters:
        x : float
            Value to interpret (typically time or distance)
            
        Returns:
        str : Interpretation of the exponential value
        """
        rate = self.rate()
        mean = self.mean()
        p_less = self.cdf(x)
        p_greater = self.sf(x)
        
        result = f"Value x = {x:.4f}\n"
        result += f"Rate (λ) = {rate:.4f}\n"
        result += f"Mean (1/λ) = {mean:.4f}\n\n"
        
        result += f"Probability of waiting time ≤ {x:.4f}: {p_less:.4f}\n"
        result += f"Probability of waiting time > {x:.4f}: {p_greater:.4f}\n\n"
        
        if x < mean:
            result += f"This value is less than the mean waiting time ({mean:.4f}).\n"
            result += f"It represents a relatively short waiting time.\n"
        elif x > 2 * mean:
            result += f"This value is more than twice the mean waiting time ({mean:.4f}).\n"
            result += f"It represents an unusually long waiting time.\n"
        else:
            result += f"This value is comparable to the mean waiting time ({mean:.4f}).\n"
            result += f"It represents a typical waiting time.\n"
        
        # Memoryless property interpretation
        result += "\nMemoryless Property:\n"
        result += f"The probability of waiting more than {x:.4f} additional units, given that\n"
        result += f"we've already waited for any time t, equals {np.exp(-rate*x):.4f}.\n"
        
        return result


class PoissonDistribution(Distribution):
    """Poisson distribution"""
    
    def __init__(self, mu: float, loc: float = 0):
        """Initialize a Poisson distribution
        
        Parameters:
        mu : float
            Rate parameter (mean)
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.poisson(mu, loc=loc)
        self.params = {'mu': mu, 'loc': loc}
        self.name = "Poisson"
        self.continuous = False
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        mu = self.params['mu']
        loc = self.params['loc']
        upper = loc + max(mu + 4 * np.sqrt(mu), 10)
        return (loc, upper)
    
    def interpret(self, k: int) -> str:
        """Interpret Poisson distribution value
        
        Parameters:
        k : int
            Number of events to interpret
            
        Returns:
        str : Interpretation of the Poisson value
        """
        mu = self.params['mu']
        p_exactly_k = self.pmf(k)
        p_at_most_k = self.cdf(k)
        p_more_than_k = self.sf(k)
        
        result = f"Number of events k = {k}\n"
        result += f"Expected number of events (μ) = {mu:.4f}\n\n"
        
        result += f"Probability of exactly {k} events: {p_exactly_k:.6f}\n"
        result += f"Probability of at most {k} events: {p_at_most_k:.6f}\n"
        result += f"Probability of more than {k} events: {p_more_than_k:.6f}\n\n"
        
        result += "INTERPRETATION:\n"
        if k == 0:
            result += f"This represents no events occurring in the interval.\n"
            result += f"With rate μ={mu:.4f}, this has probability {p_exactly_k:.6f}.\n"
        elif k < mu:
            result += f"This value is below the expected number of events ({mu:.4f}).\n"
            result += f"It represents fewer events than typically expected.\n"
        elif k > mu + 2 * np.sqrt(mu):
            result += f"This value is well above the expected number ({mu:.4f}).\n"
            result += f"It represents an unusually high number of events.\n"
        else:
            result += f"This value is near the expected number of events ({mu:.4f}).\n"
            result += f"It represents a typical occurrence for this process.\n"
        
        # Rare event interpretation
        if p_exactly_k < 0.01:
            result += f"\nThis specific outcome (exactly {k} events) is quite rare (probability < 1%).\n"
        elif p_exactly_k < 0.05:
            result += f"\nThis specific outcome (exactly {k} events) is relatively uncommon (probability < 5%).\n"
        
        return result


class BinomialDistribution(Distribution):
    """Binomial distribution"""
    
    def __init__(self, n: int, p: float, loc: float = 0):
        """Initialize a Binomial distribution
        
        Parameters:
        n : int
            Number of trials
        p : float
            Probability of success in a single trial
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.binom(n, p, loc=loc)
        self.params = {'n': n, 'p': p, 'loc': loc}
        self.name = "Binomial"
        self.continuous = False
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        n = self.params['n']
        p = self.params['p']
        loc = self.params['loc']
        mean = n * p
        std = np.sqrt(n * p * (1 - p))
        lower = max(0, loc + int(mean - 3 * std))
        upper = min(n, loc + int(mean + 3 * std))
        return (lower, upper)
    
    def interpret(self, k: int) -> str:
        """Interpret binomial distribution value
        
        Parameters:
        k : int
            Number of successes to interpret
            
        Returns:
        str : Interpretation of the binomial value
        """
        n = self.params['n']
        p = self.params['p']
        expected = n * p
        p_exactly_k = self.pmf(k)
        p_at_most_k = self.cdf(k)
        p_at_least_k = self.sf(k-1) if k > 0 else 1
        
        result = f"Number of successes k = {k} out of n = {n} trials\n"
        result += f"Probability of success p = {p:.4f}\n"
        result += f"Expected number of successes = {expected:.4f}\n\n"
        
        result += f"Probability of exactly {k} successes: {p_exactly_k:.6f}\n"
        result += f"Probability of at most {k} successes: {p_at_most_k:.6f}\n"
        result += f"Probability of at least {k} successes: {p_at_least_k:.6f}\n\n"
        
        result += "INTERPRETATION:\n"
        success_rate = k / n
        result += f"Observed success rate: {success_rate:.4f}\n"
        
        if abs(k - expected) > 2 * np.sqrt(n * p * (1-p)):
            result += f"This outcome is more than 2 standard deviations from the expected value.\n"
            result += f"It is significantly {'above' if k > expected else 'below'} average and quite unusual.\n"
        elif abs(k - expected) > np.sqrt(n * p * (1-p)):
            result += f"This outcome is more than 1 standard deviation from the expected value.\n"
            result += f"It is somewhat {'above' if k > expected else 'below'} average.\n"
        else:
            result += f"This outcome is close to the expected value ({expected:.1f}).\n"
            result += f"It is within the typical range of variation.\n"
        
        # Practical significance
        if n > 30 and abs(success_rate - p) > 0.1:
            result += f"\nThe observed success rate differs from the expected rate by more than 10%.\n"
            result += f"This may indicate a systematic difference or unusual sample.\n"
        
        return result


class UniformDistribution(Distribution):
    """Uniform distribution"""
    
    def __init__(self, a: float = 0, b: float = 1):
        """Initialize a Uniform distribution
        
        Parameters:
        a : float, optional
            Lower bound. Default is 0.
        b : float, optional
            Upper bound. Default is 1.
        """
        super().__init__()
        self.dist = stats.uniform(loc=a, scale=b-a)
        self.params = {'a': a, 'b': b}
        self.name = "Uniform"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        a = self.params['a']
        b = self.params['b']
        # Add a small margin for clarity
        margin = (b - a) * 0.05
        return (a - margin, b + margin)


class BetaDistribution(Distribution):
    """Beta distribution"""
    
    def __init__(self, a: float, b: float, loc: float = 0, scale: float = 1):
        """Initialize a Beta distribution
        
        Parameters:
        a : float
            First shape parameter (alpha)
        b : float
            Second shape parameter (beta)
        loc : float, optional
            Location parameter. Default is 0.
        scale : float, optional
            Scale parameter. Default is 1.
        """
        super().__init__()
        self.dist = stats.beta(a, b, loc=loc, scale=scale)
        self.params = {'a': a, 'b': b, 'loc': loc, 'scale': scale}
        self.name = "Beta"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        loc = self.params['loc']
        scale = self.params['scale']
        # Beta is defined on [0, 1], scaled by 'scale' and shifted by 'loc'
        margin = 0.05 * scale  # Add a small margin for clarity
        return (loc - margin, loc + scale + margin)


class GammaDistribution(Distribution):
    """Gamma distribution"""
    
    def __init__(self, a: float, loc: float = 0, scale: float = 1):
        """Initialize a Gamma distribution
        
        Parameters:
        a : float
            Shape parameter (k)
        loc : float, optional
            Location parameter. Default is 0.
        scale : float, optional
            Scale parameter (theta). Default is 1.
        """
        super().__init__()
        self.dist = stats.gamma(a, loc=loc, scale=scale)
        self.params = {'a': a, 'loc': loc, 'scale': scale}
        self.name = "Gamma"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        a = self.params['a']
        loc = self.params['loc']
        scale = self.params['scale']
        # Mean = a * scale, var = a * scale^2
        mean = a * scale
        std = np.sqrt(a) * scale
        upper = loc + mean + 4 * std
        return (loc, upper)


class LogNormalDistribution(Distribution):
    """Log-normal distribution"""
    
    def __init__(self, mu: float = 0, sigma: float = 1, loc: float = 0):
        """Initialize a Log-normal distribution
        
        Parameters:
        mu : float, optional
            Mean of the underlying normal distribution. Default is 0.
        sigma : float, optional
            Standard deviation of the underlying normal distribution. Default is 1.
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.lognorm(s=sigma, scale=np.exp(mu), loc=loc)
        self.params = {'mu': mu, 'sigma': sigma, 'loc': loc}
        self.name = "Log-normal"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        mu = self.params['mu']
        sigma = self.params['sigma']
        loc = self.params['loc']
        # Log-normal is right-skewed
        mean = np.exp(mu + sigma**2/2)
        var = (np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2)
        std = np.sqrt(var)
        upper = loc + mean + 4 * std
        return (loc, upper)


class GeometricDistribution(Distribution):
    """Geometric distribution"""
    
    def __init__(self, p: float, loc: float = 0):
        """Initialize a Geometric distribution
        
        Parameters:
        p : float
            Probability of success in a single trial
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.geom(p, loc=loc)
        self.params = {'p': p, 'loc': loc}
        self.name = "Geometric"
        self.continuous = False
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        p = self.params['p']
        loc = self.params['loc']
        # Mean = 1/p, var = (1-p)/p^2
        mean = 1/p
        std = np.sqrt((1-p)/p**2)
        upper = loc + int(mean + 4 * std)
        return (loc, upper)


class WeibullDistribution(Distribution):
    """Weibull distribution"""
    
    def __init__(self, c: float, loc: float = 0, scale: float = 1):
        """Initialize a Weibull distribution
        
        Parameters:
        c : float
            Shape parameter (k)
        loc : float, optional
            Location parameter. Default is 0.
        scale : float, optional
            Scale parameter (lambda). Default is 1.
        """
        super().__init__()
        self.dist = stats.weibull_min(c, loc=loc, scale=scale)
        self.params = {'c': c, 'loc': loc, 'scale': scale}
        self.name = "Weibull"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        c = self.params['c']
        loc = self.params['loc']
        scale = self.params['scale']
        # Use gamma function to calculate mean and variance
        mean = scale * np.exp(np.log(1 + 1/c))
        var = scale**2 * (np.exp(np.log(1 + 2/c)) - np.exp(2*np.log(1 + 1/c)))
        std = np.sqrt(var)
        upper = loc + mean + 4 * std
        return (loc, upper)


class CauchyDistribution(Distribution):
    """Cauchy distribution"""
    
    def __init__(self, loc: float = 0, scale: float = 1):
        """Initialize a Cauchy distribution
        
        Parameters:
        loc : float, optional
            Location parameter. Default is 0.
        scale : float, optional
            Scale parameter. Default is 1.
        """
        super().__init__()
        self.dist = stats.cauchy(loc=loc, scale=scale)
        self.params = {'loc': loc, 'scale': scale}
        self.name = "Cauchy"
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        loc = self.params['loc']
        scale = self.params['scale']
        # Cauchy has heavy tails, so use wider range
        return (loc - 10*scale, loc + 10*scale)


class NegativeBinomialDistribution(Distribution):
    """Negative Binomial distribution"""
    
    def __init__(self, n: float, p: float, loc: float = 0):
        """Initialize a Negative Binomial distribution
        
        Parameters:
        n : float
            Number of successes
        p : float
            Probability of success in a single trial
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.nbinom(n, p, loc=loc)
        self.params = {'n': n, 'p': p, 'loc': loc}
        self.name = "Negative Binomial"
        self.continuous = False
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        n = self.params['n']
        p = self.params['p']
        loc = self.params['loc']
        # Mean = n * (1-p) / p, var = n * (1-p) / p^2
        mean = n * (1-p) / p
        std = np.sqrt(n * (1-p) / p**2)
        upper = loc + int(mean + 4 * std)
        return (loc, upper)


class HypergeometricDistribution(Distribution):
    """Hypergeometric distribution"""
    
    def __init__(self, M: int, n: int, N: int, loc: float = 0):
        """Initialize a Hypergeometric distribution
        
        Parameters:
        M : int
            Total number of objects
        n : int
            Number of objects with the desired feature
        N : int
            Number of objects drawn
        loc : float, optional
            Location parameter. Default is 0.
        """
        super().__init__()
        self.dist = stats.hypergeom(M, n, N, loc=loc)
        self.params = {'M': M, 'n': n, 'N': N, 'loc': loc}
        self.name = "Hypergeometric"
        self.continuous = False
        
    def _get_x_range(self) -> Tuple[float, float]:
        """Get a reasonable x-range for plotting"""
        M = self.params['M']
        n = self.params['n']
        N = self.params['N']
        loc = self.params['loc']
        # Mean = N * n / M, var = N * n * (M-n) * (M-N) / (M^2 * (M-1))
        mean = N * n / M
        var = N * n * (M-n) * (M-N) / (M**2 * (M-1)) if M > 1 else 0
        std = np.sqrt(var)
        lower = max(0, loc + int(mean - 3 * std))
        upper = min(N, loc + int(mean + 3 * std))
        return (lower, upper)


#-----------------------------------------------------------------
# Statistical Tests with Improved Structure
#-----------------------------------------------------------------

class StatTest(ABC):
    """Base class for statistical tests"""
    
    def __init__(self):
        """Initialize a statistical test"""
        self.name = "Generic Statistical Test"
        self.result = None
        self.statistic = None
        self.p_value = None
        self.hypothesis = {
            'null': "Generic null hypothesis",
            'alternative': "Generic alternative hypothesis"
        }
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Tuple[float, float]:
        """Run the statistical test"""
        pass
    
    def interpret(self, alpha: float = 0.05) -> str:
        """Interpret the test results
        
        Parameters:
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        str : Interpretation of the test result
        """
        if self.p_value is None:
            return "Test has not been run yet."
        
        result = self._format_test_statistics()
        result += self._make_decision(alpha)
            
        return result
    
    def _format_test_statistics(self) -> str:
        """Format the test statistics for interpretation"""
        return f"Test statistic: {self.statistic:.4f}\nP-value: {self.p_value:.4f}\n\n"
    
    def _make_decision(self, alpha: float) -> str:
        """Make a decision based on the p-value and significance level"""
        if self.p_value <= alpha:
            return f"At significance level {alpha}, we reject the null hypothesis."
        else:
            return f"At significance level {alpha}, we fail to reject the null hypothesis."
    
    def __repr__(self) -> str:
        """String representation of the test"""
        if self.result is None:
            return f"{self.name} (not run)"
        return f"{self.name}: statistic={self.statistic:.4f}, p-value={self.p_value:.4f}"


class TTest(StatTest):
    """Student's t-test"""
    
    def __init__(self, test_type: str = 'two-sided'):
        """Initialize a t-test
        
        Parameters:
        test_type : str, optional
            Type of test: 'two-sided', 'less', or 'greater'. Default is 'two-sided'.
        """
        super().__init__()
        self.name = "Student's t-test"
        self.test_type = test_type
        
        self._set_hypotheses()
    
    def _set_hypotheses(self) -> None:
        """Set up null and alternative hypotheses based on test type"""
        self.hypothesis = {
            'null': "The means are equal",
            'alternative': {
                'two-sided': "The means are not equal",
                'less': "The mean of the first sample is less than the mean of the second sample",
                'greater': "The mean of the first sample is greater than the mean of the second sample"
            }[self.test_type]
        }
    
    def run(self, sample1: np.ndarray, sample2: Optional[np.ndarray] = None, 
           popmean: float = 0) -> Tuple[float, float]:
        """Run the t-test
        
        Parameters:
        sample1 : array-like
            First sample
        sample2 : array-like, optional
            Second sample for independent t-test. Default is None.
        popmean : float, optional
            Population mean for one-sample t-test. Default is 0.
            
        Returns:
        tuple : (test statistic, p-value)
        """
        if sample2 is None:
            self._run_one_sample_test(sample1, popmean)
        else:
            self._run_two_sample_test(sample1, sample2)
        
        return (self.statistic, self.p_value)
    
    def _run_one_sample_test(self, sample: np.ndarray, popmean: float) -> None:
        """Run a one-sample t-test"""
        self.result = stats.ttest_1samp(sample, popmean, alternative=self.test_type)
        self.statistic = self.result.statistic
        self.p_value = self.result.pvalue
        self.hypothesis['null'] = f"The population mean equals {popmean}"
    
    def _run_two_sample_test(self, sample1: np.ndarray, sample2: np.ndarray) -> None:
        """Run a two-sample t-test"""
        self.result = stats.ttest_ind(sample1, sample2, alternative=self.test_type)
        self.statistic = self.result.statistic
        self.p_value = self.result.pvalue


import numpy as np
import scipy.stats as stats
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison
from scipy.stats import f
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.power import FTestAnovaPower

class ANOVA(StatTest):
    """Analysis of Variance (ANOVA) with comprehensive functionality"""
    
    def __init__(self):
        """Initialize an ANOVA test"""
        super().__init__()
        self.name = "ANOVA"
        self.hypothesis = {
            'null': "All group means are equal",
            'alternative': "At least one group mean is different"
        }
        self.groups = None
        self.group_means = None
        self.overall_mean = None
        self.effects = None
        self.sum_of_squares = None
        self.residuals = None
        self.fitted_values = None
        
    def run(self, *samples: np.ndarray) -> Tuple[float, float]:
        """Run the ANOVA test"""
        self.groups = [np.array(group) for group in samples]
        self.result = stats.f_oneway(*samples)
        self.statistic = self.result.statistic
        self.p_value = self.result.pvalue
        
        self._calculate_effects()
        self._calculate_sum_of_squares()
        self._calculate_residuals()
        
        return (self.statistic, self.p_value)
    
    def _calculate_effects(self):
        """Calculate group means, overall mean, and effects"""
        self.group_means = [np.mean(group) for group in self.groups]
        all_values = np.concatenate(self.groups)
        self.overall_mean = np.mean(all_values)
        self.effects = [mean - self.overall_mean for mean in self.group_means]
    
    def _calculate_sum_of_squares(self):
        """Calculate sum of squares for ANOVA table"""
        all_values = np.concatenate(self.groups)
        
        sst = np.sum((all_values - self.overall_mean) ** 2)
        
        ssb = 0
        for i, group in enumerate(self.groups):
            ssb += len(group) * (self.group_means[i] - self.overall_mean) ** 2
        
        ssw = sst - ssb
        
        self.sum_of_squares = {
            'total': sst,
            'between': ssb,
            'within': ssw
        }
    
    def _calculate_residuals(self):
        """Calculate residuals and fitted values"""
        self.residuals = []
        self.fitted_values = []
        
        for i, group in enumerate(self.groups):
            for value in group:
                self.residuals.append(value - self.group_means[i])
                self.fitted_values.append(self.group_means[i])
        
        self.residuals = np.array(self.residuals)
        self.fitted_values = np.array(self.fitted_values)
    
    def get_effects(self) -> Dict[str, float]:
        """Get the effects for each group"""
        if self.effects is None:
            raise ValueError("ANOVA test has not been run yet")
        
        return {f"Group_{i+1}": effect for i, effect in enumerate(self.effects)}
    
    def get_means(self) -> Dict[str, float]:
        """Get means for each group and overall mean"""
        if self.group_means is None:
            raise ValueError("ANOVA test has not been run yet")
        
        result = {f"Group_{i+1}": mean for i, mean in enumerate(self.group_means)}
        result["Overall_mean"] = self.overall_mean
        
        return result
    
    def get_error_std(self) -> float:
        """Calculate error standard deviation"""
        if self.sum_of_squares is None:
            raise ValueError("ANOVA test has not been run yet")
        
        n = sum(len(group) for group in self.groups)
        k = len(self.groups)
        df_within = n - k
        
        mse = self.sum_of_squares['within'] / df_within
        return np.sqrt(mse)
    
    def get_anova_table(self) -> pd.DataFrame:
        """Get complete ANOVA table"""
        if self.sum_of_squares is None:
            raise ValueError("ANOVA test has not been run yet")
        
        k = len(self.groups)
        n = sum(len(group) for group in self.groups)
        
        df_between = k - 1
        df_within = n - k
        df_total = n - 1
        
        ms_between = self.sum_of_squares['between'] / df_between
        ms_within = self.sum_of_squares['within'] / df_within
        
        anova_table = pd.DataFrame({
            'Source': ['Between Groups', 'Within Groups', 'Total'],
            'SS': [self.sum_of_squares['between'], 
                   self.sum_of_squares['within'], 
                   self.sum_of_squares['total']],
            'df': [df_between, df_within, df_total],
            'MS': [ms_between, ms_within, None],
            'F': [self.statistic, None, None],
            'p-value': [self.p_value, None, None]
        })
        
        return anova_table
    
    def effect_size(self) -> Dict[str, float]:
        """Calculate effect sizes"""
        if self.sum_of_squares is None:
            raise ValueError("ANOVA test has not been run yet")
        
        eta_squared = self.sum_of_squares['between'] / self.sum_of_squares['total']
        
        partial_eta_squared = self.sum_of_squares['between'] / (
            self.sum_of_squares['between'] + self.sum_of_squares['within'])
        
        k = len(self.groups)
        n = sum(len(group) for group in self.groups)
        mse = self.sum_of_squares['within'] / (n - k)
        
        omega_squared = (self.sum_of_squares['between'] - (k - 1) * mse) / (
            self.sum_of_squares['total'] + mse)
        
        return {
            'eta_squared': eta_squared,
            'partial_eta_squared': partial_eta_squared,
            'omega_squared': omega_squared
        }
    
    def post_hoc_tukey(self, alpha: float = 0.05) -> Any:
        """Perform Tukey's HSD post-hoc test"""
        all_data = []
        all_labels = []
        
        for i, group in enumerate(self.groups):
            all_data.extend(group)
            all_labels.extend([f"Group_{i+1}"] * len(group))
        
        tukey = pairwise_tukeyhsd(endog=all_data, groups=all_labels, alpha=alpha)
        return tukey
    
    def assumptions_check(self) -> Dict[str, Any]:
        """Check ANOVA assumptions"""
        results = {}
        
        normality_tests = []
        for i, group in enumerate(self.groups):
            stat, p = stats.shapiro(group)
            normality_tests.append({
                'group': f"Group_{i+1}",
                'statistic': stat,
                'p_value': p,
                'normal': p > 0.05
            })
        
        # Levene's test for homogeneity of variance
        levene_stat, levene_p = stats.levene(*self.groups)
        
        results['normality'] = normality_tests
        results['levene_test'] = {
            'statistic': levene_stat,
            'p_value': levene_p,
            'homogeneous': levene_p > 0.05
        }
        
        return results
    
    def contrast_analysis(self, contrasts: List[List[float]]) -> pd.DataFrame:
        """Perform planned contrasts analysis"""
        results = []
        
        for i, contrast in enumerate(contrasts):
            # Calculate contrast value
            contrast_value = 0
            contrast_ss = 0
            for j, (coef, group) in enumerate(zip(contrast, self.groups)):
                contrast_value += coef * np.mean(group)
                contrast_ss += (coef ** 2) / len(group)
            
            ss_contrast = contrast_value ** 2 / contrast_ss
            
            mse = self.sum_of_squares['within'] / (sum(len(g) for g in self.groups) - len(self.groups))
            f_stat = ss_contrast / mse
            p_value = 1 - f.cdf(f_stat, 1, sum(len(g) for g in self.groups) - len(self.groups))
            
            results.append({
                'contrast': f"C{i+1}",
                'value': contrast_value,
                'SS': ss_contrast,
                'F': f_stat,
                'p_value': p_value
            })
        
        return pd.DataFrame(results)
    
    def power_analysis(self, alpha: float = 0.05) -> Dict[str, float]:
        """Perform power analysis"""
        k = len(self.groups)
        n = sum(len(group) for group in self.groups)
        
        eta_squared = self.sum_of_squares['between'] / self.sum_of_squares['total']
        f_effect = np.sqrt(eta_squared / (1 - eta_squared))
        
        power_analysis = FTestAnovaPower()
        
        power = power_analysis.solve_power(
            effect_size=f_effect,
            nobs=n,
            alpha=alpha,
            k_groups=k
        )
        
        required_n = power_analysis.solve_power(
            effect_size=f_effect,
            alpha=alpha,
            power=0.8,
            k_groups=k
        )
        
        return {
            'observed_power': power,
            'effect_size_f': f_effect,
            'required_n_for_80_power': int(np.ceil(required_n))
        }
    
    def confidence_intervals(self, alpha: float = 0.05) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for group means"""
        ci_results = {}
        mse = self.sum_of_squares['within'] / (sum(len(g) for g in self.groups) - len(self.groups))
        
        for i, group in enumerate(self.groups):
            n = len(group)
            mean = np.mean(group)
            se = np.sqrt(mse / n)
            t_critical = stats.t.ppf(1 - alpha/2, n - 1)
            margin = t_critical * se
            
            ci_results[f"Group_{i+1}"] = (mean - margin, mean + margin)
        
        return ci_results
    
    def plot_diagnostics(self) -> plt.Figure:
        """Create diagnostic plots"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Residuals vs Fitted
        axes[0, 0].scatter(self.fitted_values, self.residuals)
        axes[0, 0].axhline(y=0, color='r', linestyle='--')
        axes[0, 0].set_xlabel('Fitted Values')
        axes[0, 0].set_ylabel('Residuals')
        axes[0, 0].set_title('Residuals vs Fitted')
        
        # Normal Q-Q plot
        stats.probplot(self.residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Normal Q-Q Plot')
        
        # Scale-Location plot
        standardized_residuals = np.sqrt(np.abs(self.residuals / np.std(self.residuals)))
        axes[1, 0].scatter(self.fitted_values, standardized_residuals)
        axes[1, 0].set_xlabel('Fitted Values')
        axes[1, 0].set_ylabel('√|Standardized Residuals|')
        axes[1, 0].set_title('Scale-Location Plot')
        
        # Residuals vs Group
        group_labels = []
        for i, group in enumerate(self.groups):
            group_labels.extend([i] * len(group))
        
        axes[1, 1].boxplot([self.residuals[np.array(group_labels) == i] 
                            for i in range(len(self.groups))])
        axes[1, 1].set_xlabel('Group')
        axes[1, 1].set_ylabel('Residuals')
        axes[1, 1].set_title('Residuals by Group')
        
        plt.tight_layout()
        return fig
    
    def plot_means_with_ci(self, alpha: float = 0.05) -> plt.Figure:
        """Plot group means with confidence intervals"""
        ci = self.confidence_intervals(alpha)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        groups = list(ci.keys())
        means = [self.group_means[i] for i in range(len(self.groups))]
        lower_ci = [ci[group][0] for group in groups]
        upper_ci = [ci[group][1] for group in groups]
        errors = [[means[i] - lower_ci[i] for i in range(len(means))],
                 [upper_ci[i] - means[i] for i in range(len(means))]]
        
        x_pos = range(len(groups))
        ax.errorbar(x_pos, means, yerr=errors, fmt='o', capsize=5, capthick=2)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(groups)
        ax.set_ylabel('Mean')
        ax.set_title(f'Group Means with {int((1-alpha)*100)}% Confidence Intervals')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def interpret(self, alpha: float = 0.05) -> str:
        """Interpret the ANOVA test results

        Parameters:
        alpha : float, optional
            Significance level. Default is 0.05.

        Returns:
        str : Interpretation of the ANOVA result
        """
        if self.statistic is None or self.p_value is None:
            return "ANOVA test has not been run yet."

        result = self._format_test_statistics()
        result += self._make_decision(alpha)

        result += "\n\nANOVA-Specific Interpretation:"
        result += f"\nF-statistic: {self.statistic:.4f}"

        if self.dof:
            result += f"\nDegrees of freedom: Between = {self.dof[0]}, Within = {self.dof[1]}"

        if self.statistic > 10:
            result += "\nThe large F-statistic suggests very strong evidence against the null hypothesis."
        elif self.statistic > 5:
            result += "\nThe moderate-to-large F-statistic suggests strong evidence against the null hypothesis."
        elif self.statistic > 1:
            result += "\nThe F-statistic is smaller but still indicates some difference between groups."
        else:
            result += "\nThe F-statistic is very small, suggesting minimal difference between groups."

        if self.p_value <= alpha:
            result += "\n\nPRACTICAL MEANING:"
            result += "\n- At least one group mean is significantly different from the others."
            result += "\n- The differences observed between groups are unlikely to have occurred by chance."
            result += "\n- Follow-up with post-hoc tests (e.g., Tukey's HSD) to determine which groups differ."

            if hasattr(self, 'sum_of_squares') and self.sum_of_squares is not None:
                eta_squared = self.sum_of_squares['between'] / self.sum_of_squares['total']
                result += f"\n- Effect size (eta-squared): {eta_squared:.4f}"

                if eta_squared < 0.01:
                    effect_interpretation = "negligible"
                elif eta_squared < 0.06:
                    effect_interpretation = "small"
                elif eta_squared < 0.14:
                    effect_interpretation = "medium"
                else:
                    effect_interpretation = "large"

                result += f"\n- Effect size interpretation: {effect_interpretation}"
        else:
            result += "\n\nPRACTICAL MEANING:"
            result += "\n- No significant differences were found between group means."
            result += "\n- The variation between groups is not greater than the variation within groups."
            result += "\n- Any observed differences could be due to random chance."

        result += "\n\nASSUMPTIONS TO VERIFY:"
        result += "\n- Independence of observations"
        result += "\n- Normality within each group"
        result += "\n- Homogeneity of variance (equal variances across groups)"

        return result


class ChiSquareTest(StatTest):
    """Chi-square test of independence"""
    
    def __init__(self):
        """Initialize a Chi-square test"""
        super().__init__()
        self.name = "Chi-square test"
        self.hypothesis = {
            'null': "The variables are independent",
            'alternative': "The variables are not independent"
        }
        self.dof = None
        self.expected = None
    
    def run(self, observed: np.ndarray, expected: Optional[np.ndarray] = None) -> Tuple[float, float]:
        """Run the Chi-square test
        
        Parameters:
        observed : array-like
            Observed frequencies. Can be a contingency table.
        expected : array-like, optional
            Expected frequencies. Default is None.
            
        Returns:
        tuple : (test statistic, p-value)
        """
        if expected is None:
            self._run_independence_test(observed)
        else:
            self._run_goodness_of_fit_test(observed, expected)
        
        return (self.statistic, self.p_value)
    
    def _run_independence_test(self, observed: np.ndarray) -> None:
        """Run a chi-square test of independence from contingency table"""
        self.result = stats.chi2_contingency(observed)
        self.statistic = self.result[0]
        self.p_value = self.result[1]
        # Include degrees of freedom and expected frequencies in result
        self.dof = self.result[2]
        self.expected = self.result[3]
    
    def _run_goodness_of_fit_test(self, observed: np.ndarray, expected: np.ndarray) -> None:
        """Run a chi-square goodness-of-fit test"""
        self.result = stats.chisquare(observed, expected)
        self.statistic = self.result.statistic
        self.p_value = self.result.pvalue
        self.hypothesis = {
            'null': "The observed frequencies match the expected frequencies",
            'alternative': "The observed frequencies do not match the expected frequencies"
        }
    
    def interpret(self, alpha: float = 0.05) -> str:
        """Interpret the Chi-square test results with additional details
        
        Parameters:
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        str : Interpretation of the Chi-square test result
        """
        if self.statistic is None or self.p_value is None:
            return "Chi-square test has not been run yet."
        
        result = f"Chi-square statistic: {self.statistic:.4f}\n"
        result += f"P-value: {self.p_value:.4f}\n"
        
        if self.dof is not None:
            result += f"Degrees of freedom: {self.dof}\n"
        
        result += "\nHypotheses:\n"
        result += f"H₀: {self.hypothesis['null']}\n"
        result += f"H₁: {self.hypothesis['alternative']}\n\n"
        
        if self.p_value <= alpha:
            result += f"Decision: Reject the null hypothesis at α={alpha}.\n\n"
            
            if "independent" in self.hypothesis['null'].lower():
                result += "INTERPRETATION:\n"
                result += "- There is a significant association between the variables.\n"
                result += "- The variables are NOT independent.\n"
                result += "- The observed pattern is unlikely to have occurred by chance.\n"
            else:
                result += "INTERPRETATION:\n"
                result += "- The observed frequencies significantly differ from the expected frequencies.\n"
                result += "- The data does not follow the hypothesized distribution.\n"
                result += "- The pattern deviates significantly from what was expected.\n"
        else:
            result += f"Decision: Fail to reject the null hypothesis at α={alpha}.\n\n"
            
            if "independent" in self.hypothesis['null'].lower():
                result += "INTERPRETATION:\n"
                result += "- There is no significant association between the variables.\n"
                result += "- The variables appear to be independent.\n"
                result += "- Any observed pattern could be due to random chance.\n"
            else:
                result += "INTERPRETATION:\n"
                result += "- The observed frequencies do not significantly differ from expected frequencies.\n"
                result += "- The data follows the hypothesized distribution reasonably well.\n"
                result += "- No significant deviation from the expected pattern was found.\n"
        
        if hasattr(self, 'expected') and len(self.expected.shape) == 2:
            n = np.sum(self.expected)
            min_dim = min(self.expected.shape) - 1
            cramer_v = np.sqrt(self.statistic / (n * min_dim))
            result += f"\nEffect Size (Cramer's V): {cramer_v:.4f}"
            
            if cramer_v > 0.25:
                result += " (large effect)"
            elif cramer_v > 0.15:
                result += " (medium effect)"
            elif cramer_v > 0.05:
                result += " (small effect)"
            else:
                result += " (negligible effect)"
        
        return result


#-----------------------------------------------------------------
# Utility Functions with Improved Implementation
#-----------------------------------------------------------------

def fit_distribution(data: np.ndarray, dist_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Find the best-fitting distribution for the data
    
    Parameters:
    data : array-like
        Data to fit
    dist_types : list of str, optional
        List of distribution types to try. Default is common continuous distributions.
        
    Returns:
    list of dict : List of dictionaries with distribution fits and statistics, sorted by fit quality
    """
    if dist_types is None:
        # Default to common continuous distributions
        dist_types = ['normal', 'gamma', 'lognormal', 'beta', 'weibull', 'exponential']
    
    results = []
    
    for dist_type in dist_types:
        try:
            fitted_result = _fit_single_distribution(dist_type, data)
            if fitted_result:
                results.append(fitted_result)
        except Exception as e:
            print(f"Error fitting {dist_type} distribution: {e}")
    
    # Sort results by AIC (lower is better)
    results.sort(key=lambda x: x['aic'])
    
    return results


def _fit_single_distribution(dist_type: str, data: np.ndarray) -> Optional[Dict[str, Any]]:
    """Fit a single distribution type to data and compute goodness-of-fit metrics
    
    Parameters:
    dist_type : str
        Distribution type to fit
    data : array-like
        Data to fit the distribution to
        
    Returns:
    dict or None : Dictionary with fitted distribution and statistics, or None if fitting failed
    """
    # Create the distribution
    dist = distribution(dist_type)
    
    # Fit distribution parameters using MLE
    params = dist.fit(data)
    
    # Reconfigure the distribution with fitted parameters
    fitted_dist = _create_fitted_distribution(dist_type, params)
    
    if fitted_dist is None:
        return None
    
    # Calculate goodness-of-fit statistics
    return _calculate_fit_statistics(fitted_dist, data, params)


def _create_fitted_distribution(dist_type: str, params: Tuple) -> Optional[Distribution]:
    """Create a distribution with fitted parameters
    
    Parameters:
    dist_type : str
        Distribution type
    params : tuple
        Fitted parameters
        
    Returns:
    Distribution or None : Configured distribution object or None if creation failed
    """
    try:
        if dist_type in ['normal', 'gaussian', 'norm']:
            return distribution(dist_type, mu=params[0], sigma=params[1])
        elif dist_type in ['gamma']:
            return distribution(dist_type, a=params[0], loc=params[1], scale=params[2])
        elif dist_type in ['lognormal', 'lognorm']:
            # For lognorm, s is sigma and scale is exp(mu)
            s = params[0]
            loc = params[1]
            scale = params[2]
            mu = np.log(scale)
            return distribution(dist_type, mu=mu, sigma=s, loc=loc)
        elif dist_type in ['beta']:
            return distribution(dist_type, a=params[0], b=params[1], loc=params[2], scale=params[3])
        elif dist_type in ['weibull']:
            return distribution(dist_type, c=params[0], loc=params[1], scale=params[2])
        elif dist_type in ['exponential', 'exp']:
            return distribution(dist_type, scale=params[1], loc=params[0])
        else:
            # For other distributions, just use the parameters as-is
            return distribution(dist_type, *params)
    except Exception:
        return None


def _calculate_fit_statistics(distribution: Distribution, data: np.ndarray, 
                            params: Tuple) -> Dict[str, Any]:
    """Calculate goodness-of-fit statistics for a fitted distribution
    
    Parameters:
    distribution : Distribution
        Fitted distribution object
    data : array-like
        Data the distribution was fitted to
    params : tuple
        Fitted parameters
        
    Returns:
    dict : Dictionary with fit statistics
    """
    # Kolmogorov-Smirnov test
    ks_stat, ks_pval = stats.kstest(data, distribution.cdf)
    
    # AIC (Akaike Information Criterion)
    # Approximate AIC for continuous distributions
    n = len(data)
    k = len(params)  # Number of parameters
    log_likelihood = np.sum(np.log(distribution.pdf(data) + 1e-10))  # Add small value to avoid log(0)
    aic = 2 * k - 2 * log_likelihood
    
    # Store results
    return {
        'distribution': distribution,
        'params': distribution.params,
        'ks_stat': ks_stat,
        'ks_pval': ks_pval,
        'aic': aic
    }


def compare_distributions(data: np.ndarray, 
                         dist_list: Optional[List[Distribution]] = None) -> pd.DataFrame:
    """Compare multiple distributions for fitting to data
    
    Parameters:
    data : array-like
        Data to fit
    dist_list : list of Distribution objects, optional
        List of pre-configured distributions to compare. Default is None.
        
    Returns:
    pandas.DataFrame : Comparison table of fit statistics
    """
    if dist_list is None:
        # Fit common distributions and use those
        fitted_results = fit_distribution(data)
        dist_list = [result['distribution'] for result in fitted_results]
    
    results = []
    
    for dist in dist_list:
        # Calculate and store fit metrics
        result = _calculate_distribution_fit_metrics(dist, data)
        results.append(result)
    
    # Convert to DataFrame and sort by AIC
    results_df = pd.DataFrame(results)
    return results_df.sort_values('aic')


def _calculate_distribution_fit_metrics(dist: Distribution, data: np.ndarray) -> Dict[str, Any]:
    """Calculate fit metrics for a distribution on data
    
    Parameters:
    dist : Distribution
        Distribution to evaluate
    data : array-like
        Data to compare with
        
    Returns:
    dict : Dictionary with fit metrics
    """
    # Calculate goodness-of-fit statistics
    ks_stat, ks_pval = stats.kstest(data, dist.cdf)
    
    # For discrete distributions, calculate Chi-square statistic
    chi2_stat, chi2_pval = _calculate_chi_square_metric(dist, data)
    
    # Calculate information criteria
    n = len(data)
    k = len(dist.params)
    log_likelihood = np.sum(np.log(dist.pdf(data) + 1e-10))
    aic = 2 * k - 2 * log_likelihood
    bic = k * np.log(n) - 2 * log_likelihood
    
    # Return all metrics
    return {
        'distribution': dist.name,
        'params': str(dist.params),
        'ks_stat': ks_stat,
        'ks_pval': ks_pval,
        'chi2_stat': chi2_stat,
        'chi2_pval': chi2_pval,
        'aic': aic,
        'bic': bic,
        'log_likelihood': log_likelihood
    }


def _calculate_chi_square_metric(dist: Distribution, data: np.ndarray) -> Tuple[float, float]:
    """Calculate Chi-square statistics for distribution fit
    
    Parameters:
    dist : Distribution
        Distribution to evaluate
    data : array-like
        Data to compare with
        
    Returns:
    tuple : (chi-square statistic, p-value)
    """
    if not dist.continuous:
        try:
            # Count observed frequencies
            observed = pd.Series(data).value_counts().sort_index()
            
            # Calculate expected frequencies
            x_values = observed.index.values
            expected = dist.pmf(x_values) * len(data)
            
            # Chi-square test
            valid_bins = expected >= 5
            if sum(valid_bins) > 5:
                chi2_stat, chi2_pval = stats.chisquare(
                    observed[valid_bins], 
                    expected[valid_bins]
                )
                return chi2_stat, chi2_pval
        except Exception:
            pass
    
    return np.nan, np.nan


def plot_multiple_distributions(distributions: List[Distribution], 
                              x_range: Optional[Tuple[float, float]] = None, 
                              num_points: int = 1000, 
                              figsize: Tuple[int, int] = (10, 6), 
                              title: Optional[str] = None, 
                              **kwargs) -> plt.Figure:
    """Plot multiple probability density/mass functions on the same graph
    
    Parameters:
    distributions : list of Distribution objects
        Distributions to plot
    x_range : tuple, optional
        Range (min, max) for x-axis. Default is based on distribution parameters.
    num_points : int, optional
        Number of points to plot for continuous distributions. Default is 1000.
    figsize : tuple, optional
        Figure size. Default is (10, 6).
    title : str, optional
        Plot title. Default is None.
    **kwargs :
        Additional keyword arguments to pass to plotting functions.
        
    Returns:
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Determine x_range if not provided
    x_range = _determine_combined_x_range(distributions, x_range)
    
    # Check distribution types
    distribution_types = _analyze_distribution_types(distributions)
    
    if distribution_types['all_continuous']:
        _plot_continuous_distributions(ax, distributions, x_range, num_points)
    elif distribution_types['all_discrete']:
        _plot_discrete_distributions(ax, distributions, x_range)
    else:
        _plot_mixed_distributions(ax, distributions, x_range, num_points)
    
    # Set plot aesthetics
    _set_plot_aesthetics(ax, distributions, title)
    
    return fig


def _determine_combined_x_range(distributions: List[Distribution], 
                              x_range: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
    """Determine the combined x-range for multiple distributions"""
    if x_range is None:
        # Find min and max from all distributions
        mins = []
        maxes = []
        for dist in distributions:
            dist_range = dist._get_x_range()
            mins.append(dist_range[0])
            maxes.append(dist_range[1])
        return (min(mins), max(maxes))
    return x_range


def _analyze_distribution_types(distributions: List[Distribution]) -> Dict[str, bool]:
    """Analyze the types of distributions in the list"""
    all_continuous = all(dist.continuous for dist in distributions)
    all_discrete = all(not dist.continuous for dist in distributions)
    
    return {
        'all_continuous': all_continuous,
        'all_discrete': all_discrete,
        'mixed': not (all_continuous or all_discrete)
    }


def _plot_continuous_distributions(ax: plt.Axes, distributions: List[Distribution],
                                 x_range: Tuple[float, float], num_points: int) -> None:
    """Plot multiple continuous distributions"""
    x = np.linspace(x_range[0], x_range[1], num_points)
    for dist in distributions:
        ax.plot(x, dist.pdf(x), label=str(dist))


def _plot_discrete_distributions(ax: plt.Axes, distributions: List[Distribution],
                               x_range: Tuple[float, float]) -> None:
    """Plot multiple discrete distributions"""
    x = np.arange(x_range[0], x_range[1] + 1)
    bar_width = 0.8 / len(distributions)
    offsets = np.linspace(-0.4, 0.4, len(distributions))
    
    for i, dist in enumerate(distributions):
        ax.bar(x + offsets[i], dist.pmf(x), width=bar_width, 
              alpha=0.7, label=str(dist))


def _plot_mixed_distributions(ax: plt.Axes, distributions: List[Distribution],
                            x_range: Tuple[float, float], num_points: int) -> None:
    """Plot a mix of continuous and discrete distributions"""
    x_cont = np.linspace(x_range[0], x_range[1], num_points)
    x_disc = np.arange(x_range[0], x_range[1] + 1)
    
    for dist in distributions:
        if dist.continuous:
            ax.plot(x_cont, dist.pdf(x_cont), label=str(dist))
        else:
            ax.bar(x_disc, dist.pmf(x_disc), width=0.1, 
                  alpha=0.5, label=str(dist))


def _set_plot_aesthetics(ax: plt.Axes, distributions: List[Distribution], 
                       title: Optional[str] = None) -> None:
    """Set aesthetics for the multiple distribution plot"""
    if title is None:
        title = "Comparison of Probability Distributions"
    
    ax.set_title(title)
    ax.set_xlabel('x')
    ax.set_ylabel('Density/Probability')
    ax.legend()
    ax.grid(True, alpha=0.3)


#-----------------------------------------------------------------
# Testing Framework
#-----------------------------------------------------------------

class DistributionTest:
    """Class for testing distribution implementations"""
    
    @staticmethod
    def test_interface(dist: Distribution) -> Dict[str, bool]:
        """Test if a distribution implements all required methods
        
        Parameters:
        dist : Distribution
            Distribution to test
            
        Returns:
        dict : Results of interface tests
        """
        results = {}
        
        # Test required methods
        required_methods = [
            'pdf', 'cdf', 'sf', 'ppf', 'isf', 'mean', 'var', 'std',
            'random', 'describe', '_get_x_range'
        ]
        
        for method in required_methods:
            results[f'has_{method}'] = hasattr(dist, method) and callable(getattr(dist, method))
        
        # Test if discrete distributions have pmf
        if not dist.continuous:
            results['has_pmf'] = hasattr(dist, 'pmf') and callable(getattr(dist, 'pmf'))
        
        return results
    
    @staticmethod
    def test_properties(dist: Distribution) -> Dict[str, Any]:
        """Test property calculations of a distribution
        
        Parameters:
        dist : Distribution
            Distribution to test
            
        Returns:
        dict : Results of property tests
        """
        results = {}
        
        # Test basic properties
        try:
            results['mean'] = dist.mean()
            results['variance'] = dist.var()
            results['std'] = dist.std()
            results['median'] = dist.median()
            
            # Check if mean, median calculation is correct
            if dist.continuous:
                # For continuous, median CDF should be 0.5
                median_check = abs(dist.cdf(dist.median()) - 0.5) < 1e-10
                results['median_check'] = median_check
            
            # Generate random samples
            samples = dist.random(size=1000)
            results['sample_mean'] = np.mean(samples)
            results['sample_std'] = np.std(samples)
            
            # Check if sample mean is close to distribution mean (within 3 std errors)
            if not np.isnan(results['mean']) and not np.isinf(results['mean']):
                std_error = results['std'] / np.sqrt(1000)
                mean_diff = abs(results['sample_mean'] - results['mean'])
                results['mean_within_3se'] = mean_diff < 3 * std_error
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    @staticmethod
    def test_fitting(dist: Distribution, n_samples: int = 1000) -> Dict[str, Any]:
        """Test parameter fitting on simulated data
        
        Parameters:
        dist : Distribution
            Distribution to test
        n_samples : int, optional
            Number of samples to generate. Default is 1000.
            
        Returns:
        dict : Results of fitting tests
        """
        results = {}
        
        try:
            # Generate samples from the distribution
            true_params = dist.params.copy()
            samples = dist.random(size=n_samples)
            
            # Fit the distribution to the samples
            if hasattr(dist, 'fit'):
                fitted_params = dist.fit(samples)
                results['fitted_params'] = fitted_params
                
                # Create a new distribution with fitted parameters
                dist_type = dist.__class__.__name__.replace('Distribution', '').lower()
                fitted_dist = distribution(dist_type, *fitted_params)
                
                # Compare log-likelihoods
                original_ll = np.sum(np.log(dist.pdf(samples) + 1e-10))
                fitted_ll = np.sum(np.log(fitted_dist.pdf(samples) + 1e-10))
                
                results['original_ll'] = original_ll
                results['fitted_ll'] = fitted_ll
                results['ll_improved'] = fitted_ll >= original_ll
            else:
                results['can_fit'] = False
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
