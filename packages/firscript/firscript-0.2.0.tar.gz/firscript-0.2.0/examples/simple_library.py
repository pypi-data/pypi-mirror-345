"""
Simple Library Script Example
Provides utility functions for other scripts
"""

def calculate_average(values):
    """Calculate the average of a list of values"""
    if not values:
        return 0
    return sum(values) / len(values)

def calculate_momentum(values, period=14):
    """Calculate momentum: current value - value 'period' bars ago"""
    if len(values) < period:
        return 0
    return values[-1] - values[-period]

def calculate_rate_of_change(values, period=14):
    """Calculate rate of change: (current / past - 1) * 100"""
    if len(values) < period or values[-period] == 0:
        return 0
    return ((values[-1] / values[-period]) - 1) * 100

# Export the functions as a dictionary
export = {
    "average": calculate_average,
    "momentum": calculate_momentum,
    "roc": calculate_rate_of_change
}
