"""Implements the main function."""

from absl import app, flags
from PIL import Image

import numpy as np
import torch
import torch.nn.functional as F

import matplotlib.pyplot as plt

flags.DEFINE_string('img_path', 'img.jpg', 'Image location')
FLAGS = flags.FLAGS

def convolve_image(img, kernel_size):
  """Convolves an image with an average filter of a given size."""
  kernel = torch.ones((1, 1, kernel_size, kernel_size)) / (kernel_size ** 2)
  
  # Add batch and channel dimensions to img
  img = img.unsqueeze(0).unsqueeze(0)
  
  # Convolve opr here.
  # Padding is set to 'same' so that output size matches input size
  output = F.conv2d(img, kernel, padding='same')
  
  # Remove batch and channel dimensions from output
  return output.squeeze(0).squeeze(0)

def main(argv):
  # Image from torchvision tutorial.
  img = np.array(Image.open(FLAGS.img_path))
  img = torch.from_numpy(img).float()[:, :, 0:3].permute(2, 0, 1).mean(0)

  fig, ax = plt.subplots(1, 3)
  for idx, k in enumerate([5, 11, 51]):
    out = convolve_image(img, k)
    ax[idx].imshow(out.numpy(), cmap="grey")
    ax[idx].set_title(f'Kernel size: {k}')
    ax[idx].axis('off')
  plt.savefig(f'{FLAGS.img_path}_smooth.png')

  plt.figure()
  # Perform edge detection using convolution.
  # The result is the difference between the original image and the convolved image.
  fig, ax = plt.subplots(1, 3)
  for idx, k in enumerate([5, 11, 51]):
    out = convolve_image(img, k)
    # edge detection here.
    out = img - out
    ax[idx].imshow(out.numpy(),cmap="grey")
    ax[idx].set_title(f'Kernel size: {k}')
    ax[idx].axis('off')
  plt.savefig(f'{FLAGS.img_path}_sharp.png')


if __name__ == '__main__':
  app.run(main)
