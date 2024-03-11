"""Implements the main function."""

from absl import app, flags
from datasets.toy_datasets import ToyDataset 
from torch.utils.data import DataLoader
from utils.visualize import visualize_samples
from model.vae import VAE, Encoder, Decoder
from model.cvae import CVAE, CEncoder, CDecoder

import torch 

flags.DEFINE_boolean('cuda', True, 'Whether to use cuda.')
flags.DEFINE_enum('dataset', 'moons',['moons', 'circles', 'blobs'], 'Dataset name')
flags.DEFINE_enum('model_name', 'cvae',['vae', 'cvae'], 'Model Name')
flags.DEFINE_float('learning_rate', 1e-3, 'Learning rate.')
flags.DEFINE_integer('batch_size', 64, 'Batch size')
flags.DEFINE_integer('num_epochs', 100, 'Number of Epochs')
flags.DEFINE_string('data_path', './data', 'Dataset location')

FLAGS = flags.FLAGS

def main(argv):
  torch.manual_seed(0)
  training_data = ToyDataset(data_name=FLAGS.dataset,data_size=2000, seed=0)
  train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True, drop_last=True)

  gt_title = f'Ground truth {FLAGS.dataset} dataset'
  visualize_samples(training_data.data, training_data.labels, title=gt_title, save_path=f'./{FLAGS.dataset}_gt.png')

  if FLAGS.model_name == 'vae':
    model = VAE(Encoder(2, 256, 20), Decoder(20, 256, 2))
  else:
    model = CVAE(CEncoder(2, 256, 20, 2), CDecoder(20, 256, 2, 2))
  if FLAGS.cuda:
    model.cuda()

  optimizer = torch.optim.Adam(model.parameters(), lr=FLAGS.learning_rate)
  for num_epoch in range(FLAGS.num_epochs):
    for x, c in train_dataloader:
      if FLAGS.cuda:
        x=x.cuda()
        c=c.cuda()
      if FLAGS.model_name == 'vae':
        x_hat, mu, logvar = model(x)
      else:
        x_hat, mu, logvar = model(x, c)
      loss = model.loss(x, x_hat, mu, logvar)
      loss.backward()
      optimizer.step()
      optimizer.zero_grad()
    print(f'Epoch {num_epoch}, Loss {loss.item()}')
  if FLAGS.model_name == 'vae':
    samples = model.sample(1000)
    title = f'Generated samples from {FLAGS.dataset} using VAE'
    save_path = f'./{FLAGS.dataset}_vae.png'
    visualize_samples(samples.cpu().detach().numpy(), torch.zeros(1000).numpy(), title=title, save_path=save_path)
  else:
    samples, c_samples = model.sample(1000)
    title = f'Generated samples from {FLAGS.dataset} using CVAE'
    save_path = f'./{FLAGS.dataset}_cvae.png'
    visualize_samples(samples.cpu().detach().numpy(), c_samples.cpu().numpy(), title=title, save_path=save_path) 
  
if __name__ == '__main__':
  app.run(main)
