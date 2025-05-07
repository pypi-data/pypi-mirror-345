import numpy as np
from scipy.ndimage import convolve1d

def route_with_maxbas(runoff_series= None, maxbas=1):
    """
    Correct linear interpolation routing as per HBV specifications
    - MAXBAS=1: No routing (weights = [1.0])
    - MAXBAS=2: Weights = [0.5, 0.5]
    - MAXBAS=3: Weights = [0.25, 0.5, 0.25]
    - MAXBAS=4: Weights = [0.125, 0.375, 0.375, 0.125]
    - And so on...
    """
    if maxbas < 1:
        raise ValueError("MAXBAS must be ≥1")
    
    # Special case - no routing
    if maxbas == 1:
        return runoff_series.copy()
    
    # Create proper weights using linear interpolation
    if maxbas % 2 == 0:  # Even MAXBAS
        n = maxbas // 2
        x = np.linspace(0.5, n - 0.5, n)
        weights = np.concatenate([x, x[::-1]]) / (n)
    else:  # Odd MAXBAS
        n = (maxbas + 1) // 2
        x = np.linspace(0.5, n - 1, n)
        weights = np.concatenate([x, x[-2::-1]]) / (n - 0.5)
    
    weights /= weights.sum()  # Ensure exact sum=1
    
    # Apply convolution
    routed = convolve1d(
        runoff_series,
        weights,
        origin=-(len(weights)//2),
        mode='constant',
        cval=0.0
    )
    
    return routed[:len(runoff_series)]