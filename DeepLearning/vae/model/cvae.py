"""Implements a CVAE."""

import torch
import torch.nn as nn
import math
from model.vae import VAE
import torch.nn.functional as F


class CEncoder(nn.Module):
  def __init__(self, input_dim, hidden_dim, latent_dim, emb_dim):
    super(CEncoder, self).__init__()
    self.input_dim = input_dim
    self.hidden_dim = hidden_dim
    self.latent_dim = latent_dim
    self.emb_dim = emb_dim
    
    self.embedding = nn.Embedding(2, emb_dim)
    
    self.fc1 = nn.Linear(input_dim + emb_dim, hidden_dim)
    self.fc_h1 = nn.Linear(hidden_dim, 2 * hidden_dim)
    self.fc_h2 = nn.Linear(2 * hidden_dim, hidden_dim)
    self.fc2 = nn.Linear(hidden_dim, latent_dim * 2)

  def forward(self, x, c):
    """Forward pass for the encoder.
    Args:
      x: torch.Tensor of shape (batch_size, input_dim)
      c: torch.Tensor of shape (batch_size,)
      Returns:
      mu: torch.Tensor of shape (batch_size, latent_dim)
      logvar: torch.Tensor of shape (batch_size, latent_dim)
    """
    c_emb = self.embedding(c.long())
    x = torch.cat([x, c_emb], dim=1)
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc_h1(x))
    x = F.relu(self.fc_h2(x))
    x = self.fc2(x)
    mu, logvar = x.chunk(2, dim=1)
    return mu, logvar


class CDecoder(nn.Module):
  def __init__(self, latent_dim, hidden_dim, output_dim, emb_dim):
    super(CDecoder, self).__init__()
    self.latent_dim = latent_dim
    self.hidden_dim = hidden_dim
    self.output_dim = output_dim
    self.emb_dim = emb_dim

    self.embedding = nn.Embedding(2, emb_dim)

    self.fc1 = nn.Linear(latent_dim+emb_dim, hidden_dim)
    self.fc_h1 = nn.Linear(hidden_dim, 2 * hidden_dim)
    self.fc_h2 = nn.Linear(2 * hidden_dim, hidden_dim)
    self.fc2 = nn.Linear(hidden_dim, output_dim)


  def forward(self, x, c):
    """Forward pass for the decoder.
    Args:
      x: torch.Tensor of shape (batch_size, latent_dim)
      c: torch.Tensor of shape (batch_size,)
    Returns:
      x_hat: torch.Tensor of shape (batch_size, output_dim)
    """
    c_emb = self.embedding(c.long())

    # x = torch.cat([x, c_emb], dim=1)
    # x = F.leaky_relu(self.fc1(x))
    # x = F.leaky_relu(self.fc_h1(x))
    # x = F.leaky_relu(self.fc_h2(x))

    x = torch.cat([x, c_emb], dim=1)
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc_h1(x))
    x = F.relu(self.fc_h2(x))
    x_hat = self.fc2(x)
    return x_hat


class CVAE(VAE):
  def __init__(self, encoder, decoder):
    super(VAE, self).__init__()
    self.encoder = encoder
    self.decoder = decoder

  def forward(self, x, c):
    """Forward pass for the CVAE.
    Args:
      x: torch.Tensor of shape (batch_size, input_dim)
      c: torch.Tensor of shape (batch_size,)
    Returns:
      x_hat: torch.Tensor of shape (batch_size, output_dim)
      mu: torch.Tensor of shape (batch_size, latent_dim)
      logvar: torch.Tensor of shape (batch_size, latent_dim)
    """
    mu, logvar = self.encoder(x, c)
    z = self.reparameterize(mu, logvar)
    x_hat = self.decoder(z, c)
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
    MSE = F.mse_loss(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    beta=0.085
    loss=MSE + beta * KLD
    return loss

  def sample(self, num_samples):
    """Sample from the VAE.
    Args:
      num_samples: int, the number of samples to generate.
    Returns:
      samples: torch.Tensor of shape (num_samples, output_dim)
      c: torch.Tensor of shape (num_samples,)
    """
    c = torch.bernoulli(0.5 * torch.ones(num_samples)).to(torch.long)
    samples = torch.randn(num_samples, self.decoder.latent_dim)
    # Decode z and c to generate samples.
    samples = self.decoder(samples, c.long()) 
    return samples, c
