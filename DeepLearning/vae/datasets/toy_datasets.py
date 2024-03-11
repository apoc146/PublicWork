"""Implements toy datasets from sklearn."""


import torch

from sklearn.datasets import make_moons, make_circles, make_blobs
from torch.utils.data import Dataset


class ToyDataset(Dataset):
  def __init__(self, data_name='moons', data_size=100, seed=0):
    self.data_name = data_name
    self.data_size = data_size
    self.seed = seed
    self.data, self.labels = self._generate_data()
    self.data = torch.from_numpy(self.data).float()
    self.labels = torch.from_numpy(self.labels).long()

  def _generate_data(self):
    if self.data_name == 'moons':
      return make_moons(n_samples=self.data_size, noise=0.1, random_state=self.seed)
    elif self.data_name == 'circles':
      return make_circles(n_samples=self.data_size, noise=0.1, random_state=self.seed)
    elif self.data_name == 'blobs':
      return make_blobs(n_samples=self.data_size, centers=2, random_state=self.seed)

  def __len__(self):
    return self.data_size

  def __getitem__(self, idx):
    return self.data[idx], self.labels[idx]
