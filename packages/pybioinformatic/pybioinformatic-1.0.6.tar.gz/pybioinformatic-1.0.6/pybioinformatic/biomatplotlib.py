"""
File: biomatplotlib.py
Description: Drawing aid library for matplotlib.
CreateDate: 2024/7/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import List
from numpy import random
import matplotlib.colors as mcolors


def generate_unique_colors(num_colors: int) -> List[str]:
    """Randomly generates a specified number of non-redundant hexadecimal color codes."""

    def __generate_unique_colors(num_colors):
        colors = set()
        while len(colors) < num_colors:
            r, g, b = random.rand(3)
            color = (r, g, b)
            colors.add(color)
        return colors

    unique_colors = __generate_unique_colors(num_colors)
    hex_colors = [mcolors.to_hex(color) for color in unique_colors]
    return hex_colors
