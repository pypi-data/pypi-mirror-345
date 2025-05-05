#!/usr/bin/env python

##  run_vae_for_image_generation.py

"""
The purpose of this script is to attempt generating images from noise vectors
AFTER you have trained the VAE Decoder.  Remember, VAE's Decoder can be 
considered to be a Generator of images from the latent distribution learned 
during the training process.

Before you get too excited by the prospect of generating images with a VAE, note
that what you will actually see are images that clearly indicate that the network
is trying to generate the sort of patterns in the training data, BUT IT DOES NOT
QUITE GET THERE.  You will see ghost-like similarity of the patterns created from
user-specified latent vectors with the patterns that were in the training dataset
when the VAE network was trained.

That you would only see ghost-like blobs in the reconstructed images is to be
expected if you consider the following reasons: (1)  The training data contains
only 20,000 images; (2)  The latent vectors reside in a 8192 dimensional space
for the network configuration used in this demo; (3) While the VAE network tries
to minimize the KL-Divergence between the zero-mean and unit-covariance standard
Gaussian and the mean and log-covariance parameters actually learned during the
training, it never quite gets there; and, last but the not the least, (4) the
number of epochs you use for training.


BEFORE YOU EXECUTE THIS SCRIPT:

Make sure that you have trained the VAE network before playing with this script.

This script assumes that the directory in which you are running this script contains
the following two models and a small data archive:


    saved_VAE_encoder_model                         around 550 MB

    saved_VAE_decoder_model                         around 26 MB 

    params_saved.p                                  around 2 MB 


This is for the Encoder and Decoder configurations that are currently in the DLStudio
implementation for VAE for demonstrating the demo presented by this script.

The Encoder is heavy because of the nn.Linear layers it needs for estimating the mean
and the log-variance of the Latent Vectors learned from the training images.   For the
network configuration that is currently programmed in the VAE class, the latent vectors
(typically denoted z) reside in a 8192 dimensional space.  The 8192 comes from the fact
that the final image produced by the Encoder (before the information is fed into the 
nn.Linear layers) is of size 8x8 and the number of channels in that layer is 128.
The vectorized representation of this output is of size 8x8x128 = 8192.

At the end of training, the final values for the mean and the log-variance of the
latent distribution are stored away for persistence in the Pickle archive 
'params_saved.p'.
"""

"""
seed = 0           
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
numpy.random.seed(seed)
torch.backends.cudnn.deterministic=True
torch.backends.cudnn.benchmarks=False
os.environ['PYTHONHASHSEED'] = str(seed)
"""

##  watch -d -n 0.5 nvidia-smi

from DLStudio import *
import os, sys


dataroot = "./dataGAN/PurdueShapes5GAN/multiobj/"
#dataroot =  "/home/kak/ImageDatasets/PurdueShapes5GAN/multiobj/"
#dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/PurdueShapes5GAN/multiobj/"


epochs = 200                            ##  Although irrelevant to pure image generation using just the
                                        ##  Decoder, better to keep it for the sake of the module calls shown below
                                      
batch_size = 48                 

learning_rate = 1e-4                    ##  Although irrelevant to pure image generation using just the
                                        ##  Decoder, better to keep it for the sake of the module calls shown below
                                
image_size = (64,64)                

encoder_out_size = (8,8)
decoder_out_size = (64,64)
encoder_out_ch = 128


dls = DLStudio(
                  dataroot = dataroot,
                  image_size = image_size,
                  learning_rate = learning_rate,        
                  epochs = epochs,
                  batch_size = batch_size,
                  use_gpu = True,
              )


vae  =  DLStudio.VAE( 
                       dl_studio = dls,
                       encoder_out_im_size = encoder_out_size,
                       decoder_out_im_size = decoder_out_size,
                       encoder_out_ch = encoder_out_ch,
                       path_saved_encoder = "./saved_VAE_encoder_model",
                       path_saved_decoder = "./saved_VAE_decoder_model",
                    )
          

number_of_learnable_params_in_vae = sum(p.numel() for p in vae.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in VAE: %d" % number_of_learnable_params_in_vae)

vae.set_dataloader()

ans =  input("""\n\nThis script assumes that your previously trained models for the\n"""
             """VAE Encoder and the VAE Decorder are already in the directory. The names of\n"""
             """these must be "saved_VAE_encoder_model" and "saved_VAE_decoder_model."\n"""
             """\n\nIs that the case? Enter 'y' for 'yes' """)
if ans == 'y':
    vae.run_code_for_generating_images_from_noise_VAE(vae, visualization_dir = "vae_gen_visualization_dir")
