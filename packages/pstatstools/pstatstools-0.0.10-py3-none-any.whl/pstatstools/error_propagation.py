import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional, Any, Callable

def propagate_error_linear(coefs: List[float], values: List[float], 
                        errors: List[float]) -> Tuple[float, float]:
    """Propagate errors through a linear combination
    
    Parameters:
    -----------
    coefs : list of float
        Coefficients for the linear combination
    values : list of float
        Variable values
    errors : list of float
        Uncertainties for each variable
        
    Returns:
    --------
    tuple : (result, uncertainty)
    """
    if len(coefs) != len(values) or len(coefs) != len(errors):
        raise ValueError("Coefficients, values, and errors must have the same length")
    result = sum(c * v for c, v in zip(coefs, values))
    variance = sum((c * e)**2 for c, e in zip(coefs, errors))
    uncertainty = np.sqrt(variance)
    
    return (result, uncertainty)


def propagate_error_product(value1: float, error1: float, value2: float, error2: float) -> Tuple[float, float]:
    """Propagate errors through a multiplication
    
    Parameters:
    -----------
    value1 : float
        Value of the first variable
    error1 : float
        Uncertainty of the first variable
    value2 : float
        Value of the second variable
    error2 : float
        Uncertainty of the second variable
        
    Returns:
    --------
    tuple : (product, uncertainty)
    """
    product = value1 * value2
    rel_variance = (error1 / value1)**2 + (error2 / value2)**2
    uncertainty = product * np.sqrt(rel_variance)
    
    return (product, uncertainty)


def propagate_error_division(value1: float, error1: float, value2: float, error2: float) -> Tuple[float, float]:
    """Propagate errors through a division
    
    Parameters:
    -----------
    value1 : float
        Value of the numerator
    error1 : float
        Uncertainty of the numerator
    value2 : float
        Value of the denominator
    error2 : float
        Uncertainty of the denominator
        
    Returns:
    --------
    tuple : (quotient, uncertainty)
    """
    quotient = value1 / value2
    rel_variance = (error1 / value1)**2 + (error2 / value2)**2
    uncertainty = quotient * np.sqrt(rel_variance)
    
    return (quotient, uncertainty)


def propagate_error_power(value: float, error: float, power: float) -> Tuple[float, float]:
    """Propagate errors through a power function
    
    Parameters:
    -----------
    value : float
        Base value
    error : float
        Uncertainty of the base
    power : float
        Exponent
        
    Returns:
    --------
    tuple : (result, uncertainty)
    """
    result = value**power
    uncertainty = abs(power * value**(power - 1)) * error
    
    return (result, uncertainty)


def propagate_error_simple(expr_type: str, values: List[float], errors: List[float]) -> Tuple[float, float]:
    """Propagate errors through simple expressions
    
    Parameters:
    -----------
    expr_type : str
        Type of expression: 'add', 'subtract', 'multiply', 'divide', 'power'
    values : list of float
        Values in the expression
    errors : list of float
        Uncertainties for each value
        
    Returns:
    --------
    tuple : (result, uncertainty)
    """
    if len(values) != len(errors):
        raise ValueError("Values and errors must have the same length")
        
    if expr_type == 'add' or expr_type == 'subtract':
        result = sum(values) if expr_type == 'add' else values[0] - sum(values[1:])
        variance = sum(e**2 for e in errors)
        uncertainty = np.sqrt(variance)
        
    elif expr_type == 'multiply' and len(values) == 2:
        result, uncertainty = propagate_error_product(values[0], errors[0], values[1], errors[1])
        
    elif expr_type == 'divide' and len(values) == 2:
        result, uncertainty = propagate_error_division(values[0], errors[0], values[1], errors[1])
        
    elif expr_type == 'power' and len(values) == 2:
        result, uncertainty = propagate_error_power(values[0], errors[0], values[1])
        
    else:
        raise ValueError(f"Unsupported expression type: {expr_type} with {len(values)} values")
        
    return (result, uncertainty)


def monte_carlo_error_propagation(func: Callable, var_dict: Dict[str, Tuple[float, float]], 
                                n_samples: int = 10000) -> Tuple[float, float]:
    """Propagate errors using Monte Carlo simulation
    
    Parameters:
    -----------
    func : callable
        Function that takes the variables as keyword arguments
    var_dict : dict
        Dictionary of variable names and their (value, uncertainty) tuples
    n_samples : int, optional
        Number of Monte Carlo samples. Default is 10000.
        
    Returns:
    --------
    tuple : (result, uncertainty)
    """
    samples = {}
    for var, (value, uncertainty) in var_dict.items():
        samples[var] = np.random.normal(value, uncertainty, n_samples)
    results = np.zeros(n_samples)
    for i in range(n_samples):
        kwargs = {var: samples[var][i] for var in var_dict}
        results[i] = func(**kwargs)
    result = np.mean(results)
    uncertainty = np.std(results, ddof=1)
    
    return (result, uncertainty)


def format_with_uncertainty(value: float, uncertainty: float, 
                           significant_digits: int = 2) -> str:
    """Format a value with its uncertainty with proper significant digits
    
    Parameters:
    -----------
    value : float
        Measured value
    uncertainty : float
        Uncertainty of the measurement
    significant_digits : int, optional
        Number of significant digits in the uncertainty. Default is 2.
        
    Returns:
    --------
    str : Formatted result
    """
    if uncertainty == 0:
        return f"{value}"
    position = -int(np.floor(np.log10(abs(uncertainty))))
    format_spec = f".{position + significant_digits - 1}f"
    rounded_value = round(value, position + significant_digits - 1)
    formatted_uncertainty = format(uncertainty, format_spec)
    formatted_value = format(rounded_value, format_spec)
    
    return f"{formatted_value} ± {formatted_uncertainty}"


def error_summary(value: float, uncertainty: float, variable_name: str = "x") -> Dict[str, Any]:
    """Generate a summary of error analysis for a measurement
    
    Parameters:
    -----------
    value : float
        Measured value
    uncertainty : float
        Uncertainty of the measurement
    variable_name : str, optional
        Name of the variable. Default is "x".
        
    Returns:
    --------
    dict : Summary statistics
    """
    if value == 0:
        relative_error = np.inf if uncertainty != 0 else 0
    else:
        relative_error = abs(uncertainty / value)
    
    percent_error = relative_error * 100
    if uncertainty > 0:
        sig_pos = -int(np.floor(np.log10(uncertainty)))
        if sig_pos < 0:
            sig_digits = 0  # integer precision
        else:
            sig_digits = sig_pos + 1
    else:
        sig_digits = 6
    formatted_value = format_with_uncertainty(value, uncertainty)
    
    return {
        'value': value,
        'uncertainty': uncertainty,
        'absolute_error': uncertainty,
        'relative_error': relative_error,
        'percent_error': percent_error,
        'significant_digits': sig_digits,
        'formatted': formatted_value,
        'variable': variable_name
    }


def calculate_combined_error(values: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate the weighted mean and its uncertainty from multiple measurements
    
    Parameters:
    -----------
    values : list of tuples
        List of (value, uncertainty) tuples
        
    Returns:
    --------
    tuple : (weighted_mean, uncertainty)
    """
    weights = [1 / (e**2) if e > 0 else 0 for _, e in values]
    total_weight = sum(weights)
    
    if total_weight == 0:
        weighted_mean = sum(v for v, _ in values) / len(values)
        uncertainty = 0
    else:
        weighted_mean = sum(w * v for w, (v, _) in zip(weights, values)) / total_weight
        uncertainty = 1 / np.sqrt(total_weight)
    
    return (weighted_mean, uncertainty)


def create_error_report(data: Dict[str, Dict[str, Union[float, Tuple[float, float]]]]) -> pd.DataFrame:
    """Create a comprehensive error report for multiple measurements
    
    Parameters:
    -----------
    data : dict
        Dictionary where keys are variable names and values are dictionaries
        with 'value', 'error', and optional additional fields
        
    Returns:
    --------
    pandas.DataFrame : Error report
    """
    report_data = []
    
    for var_name, var_data in data.items():
        value = var_data.get('value')
        error = var_data.get('error')
        
        if value is not None and error is not None:
            if value != 0:
                rel_error = abs(error / value)
                percent_error = rel_error * 100
            else:
                rel_error = np.nan
                percent_error = np.nan
            
            formatted = format_with_uncertainty(value, error)
            entry = {
                'Variable': var_name,
                'Value': value,
                'Uncertainty': error,
                'Relative Error': rel_error,
                'Percent Error (%)': percent_error,
                'Formatted': formatted
            }
            for field, field_value in var_data.items():
                if field not in ['value', 'error']:
                    entry[field] = field_value
            
            report_data.append(entry)
    df = pd.DataFrame(report_data)
    cols = ['Variable', 'Formatted', 'Value', 'Uncertainty', 'Relative Error', 'Percent Error (%)']
    other_cols = [col for col in df.columns if col not in cols]
    df = df[cols + other_cols]
    
    return df