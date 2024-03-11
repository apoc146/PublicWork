"""Implements a VAE."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math

## encoder class 
class Encoder(nn.Module):
  def __init__(self, input_dim, hidden_dim, latent_dim):
    super(Encoder, self).__init__()
    self.input_dim = input_dim
    self.hidden_dim = hidden_dim
    self.latent_dim = latent_dim
    
    # complet the model
    self.fc1 = nn.Linear(input_dim, hidden_dim)
    self.fc_h1 = nn.Linear(hidden_dim, 2*hidden_dim)
    self.fc_h2 = nn.Linear(2*hidden_dim, hidden_dim)
    self.fc2 = nn.Linear(hidden_dim, latent_dim * 2)  

  def forward(self, x):
    """Forward pass for the encoder.
    Args:
      x: torch.Tensor of shape (batch_size, input_dim)
    Returns:
      mu: torch.Tensor of shape (batch_size, latent_dim)
      logvar: torch.Tensor of shape (batch_size, latent_dim)
    """
    
    # complete the forward pass
    x = F.leaky_relu(self.fc1(x))
    x = F.leaky_relu(self.fc_h1(x))
    x = F.leaky_relu(self.fc_h2(x))
    x = self.fc2(x)
    mu, logvar = x.chunk(2, dim=1)
    return mu, logvar


class Decoder(nn.Module):
  def __init__(self, latent_dim, hidden_dim, output_dim):
    super(Decoder, self).__init__()
    self.latent_dim = latent_dim
    self.hidden_dim = hidden_dim
    self.output_dim = output_dim

    # complete the model
    self.fc1 = nn.Linear(latent_dim, hidden_dim)
    self.fc_h1 = nn.Linear(hidden_dim, 2*hidden_dim)
    self.fc_h2 = nn.Linear(2*hidden_dim, hidden_dim)
    self.fc2 = nn.Linear(hidden_dim, output_dim)

  def forward(self, x):
    """Forward pass for the decoder.
    Args:
      x: torch.Tensor of shape (batch_size, latent_dim)
    Returns:
      x_hat: torch.Tensor of shape (batch_size, output_dim)
    """
    # complete the forward pass
    x = F.leaky_relu(self.fc1(x))
    x = F.leaky_relu(self.fc_h1(x))
    x = F.leaky_relu(self.fc_h2(x))
    x_hat = self.fc2(x)
    return x_hat


class VAE(nn.Module):
  def __init__(self, encoder, decoder):
    super(VAE, self).__init__()
    self.encoder = encoder
    self.decoder = decoder

  def reparameterize(self, mu, logvar):
    """Reparameterization trick.
    Args:
      mu: torch.Tensor of shape (batch_size, latent_dim)
      logvar: torch.Tensor of shape (batch_size, latent_dim)
    Returns:
      z: torch.Tensor of shape (batch_size, latent_dim)
    """
    # reparameterization trick
    std = torch.exp(0.5*logvar)
    eps = torch.randn_like(std)
    z = mu + eps*std 
    return z

  def forward(self, x):
    """Forward pass for the VAE.
    Args:
      x: torch.Tensor of shape (batch_size, input_dim)
    Returns:
      x_hat: torch.Tensor of shape (batch_size, output_dim)
      mu: torch.Tensor of shape (batch_size, latent_dim)
      logvar: torch.Tensor of shape (batch_size, latent_dim)
    """
    # complete the forward pass
    mu, logvar = self.encoder(x)
    z = self.reparameterize(mu, logvar)
    x_hat = self.decoder(z)
    return x_hat, mu, logvar

  def loss(self, x, recon_x, mu, logvar):
    """Compute the loss function for the VAE.
    Args:
      x: torch.Tensor of shape (batch_size, input_dim)
      recon_x: torch.Tensor of shape (batch_size, output_dim)
      mu: torch.Tensor of shape (batch_size, latent_dim)
      logvar: torch.Tensor of shape (batch_size, latent_dim)
    Returns:
      loss: torch.Tensor of shape (1,)

    Hint: There is a hyperparameter in the output distribution.
    """
    # complete the loss function
    ## Use MsE loss for the reconstruction loss
    MSE = nn.functional.mse_loss(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    beta=0.085
    loss = MSE + beta*KLD
    return loss

  def sample(self, num_samples):
    """Sample from the VAE.
    Args:
      num_samples: int, the number of samples to generate.
    Returns:
      samples: torch.Tensor of shape (num_samples, output_dim)
    """
    # complete the sampling function
    samples = torch.randn(num_samples, self.decoder.latent_dim)
    samples = self.decoder(samples)
    return samples
