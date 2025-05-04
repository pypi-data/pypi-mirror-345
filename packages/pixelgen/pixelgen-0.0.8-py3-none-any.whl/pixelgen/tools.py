import numpy as np
from typing import Tuple

def create_gradient(color1: Tuple[int, int, int], 
                   color2: Tuple[int, int, int], 
                   steps: int) -> np.ndarray:
    """Create a gradient between two colors"""
    gradient = np.zeros((steps, 1, 3), dtype=np.uint8)
    for i in range(3):  # For each RGB channel
        gradient[:, 0, i] = np.linspace(color1[i], color2[i], steps, dtype=np.uint8)
    return gradient

def create_circle(radius: int, color: Tuple[int, int, int]) -> np.ndarray:
    """Create a circular pattern"""
    size = radius * 2 + 1
    pattern = np.zeros((size, size, 3), dtype=np.uint8)
    center = radius
    
    y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
    mask = x*x + y*y <= radius*radius
    
    pattern[mask] = color
    return pattern

def create_pattern(pattern_size: int, color1: Tuple[int, int, int], 
                  color2: Tuple[int, int, int]) -> np.ndarray:
    """Create a checkered pattern"""
    pattern = np.zeros((pattern_size, pattern_size, 3), dtype=np.uint8)
    for i in range(pattern_size):
        for j in range(pattern_size):
            if (i + j) % 2 == 0:
                pattern[i, j] = color1
            else:
                pattern[i, j] = color2
    return pattern

def create_dithering(width: int, height: int, 
                    color1: Tuple[int, int, int], 
                    color2: Tuple[int, int, int], 
                    pattern_type: str = "bayer") -> np.ndarray:
    """Create a dithering pattern"""
    pattern = np.zeros((height, width, 3), dtype=np.uint8)
    if pattern_type == "bayer":
        bayer_matrix = np.array([[0, 2], [3, 1]])
        for y in range(height):
            for x in range(width):
                if bayer_matrix[y % 2, x % 2] > 1:
                    pattern[y, x] = color1
                else:
                    pattern[y, x] = color2
    return pattern

def create_noise(width: int, height: int, density: float) -> np.ndarray:
    """Create noise pattern"""
    pattern = np.zeros((height, width, 3), dtype=np.uint8)
    mask = np.random.random((height, width)) < density
    pattern[mask] = [255, 255, 255]
    return pattern