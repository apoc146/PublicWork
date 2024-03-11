"""Implements visualization."""

import matplotlib.pyplot as plt
import numpy as np


def visualize_samples(X, y, title, save_path):
  plt.scatter(X[:, 0][y == 0], X[:, 1][y == 0], s=10, color='red')
  plt.scatter(X[:, 0][y == 1], X[:, 1][y == 1], s=10, color='black')
  plt.title(title)
  plt.savefig(save_path)
  plt.close()
