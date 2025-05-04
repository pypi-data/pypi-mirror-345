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
    
    def random(self, size: Union[int, Tuple[int, ...]] = 1) -> Union[float, np.ndarray]:
        """Generate random samples from the distribution
        
        Parameters:
        size : int or tuple, optional
            Output shape of samples. Default is 1.
            
        Returns:
        Random samples from the distribution
        """
        return self.dist.rvs(size=size)
    
    def rvs(self, size: Union[int, Tuple[int, ...]] = 1, 
            random_state: Optional[Union[int, np.random.RandomState]] = None) -> Union[float, np.ndarray]:
        """Generate random variates from the distribution (alias for random)"""
        return self.dist.rvs(size=size, random_state=random_state)
    
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


class ANOVA(StatTest):
    """Analysis of Variance (ANOVA)"""
    
    def __init__(self):
        """Initialize an ANOVA test"""
        super().__init__()
        self.name = "ANOVA"
        self.hypothesis = {
            'null': "All group means are equal",
            'alternative': "At least one group mean is different"
        }
    
    def run(self, *samples: np.ndarray) -> Tuple[float, float]:
        """Run the ANOVA test
        
        Parameters:
        *samples : array-like
            Two or more samples to compare
            
        Returns:
        tuple : (test statistic, p-value)
        """
        self.result = stats.f_oneway(*samples)
        self.statistic = self.result.statistic
        self.p_value = self.result.pvalue
        
        return (self.statistic, self.p_value)


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
        """Interpret the test results with additional information"""
        basic_interp = super().interpret(alpha)
        
        if self.dof is not None:
            return f"{basic_interp}\n\nDegrees of freedom: {self.dof}"
        return basic_interp


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
