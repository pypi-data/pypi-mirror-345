#!/usr/bin/env python

##  run_vae.py

"""
This script is for experimenting with the VAE (Variational Auto-Encoder) inner class in
the main DLStudio class of the DLStudio platform.

The VAE class in DLStudio is derived from the Autoencoder class.  It is the Encoder and
the Decoder in the parent class Autoencoder that does the bulk of computing in VAE. What
the VAE class does specifically is to feed the output of Autoencoder's Encoder into two
nn.Linear layers for the learning of the mean and the log-variance of the latent distribution
for the training dataset.  About decoding, VAE's Decoder invokes what's known as the 
"reparameterization trick" for sampling the latent distribution to first construct a sample 
from the latent space, reshape that sample appropriately, and to then feed it into 
Autoencoder's Decoder.


BEFORE YOU EXECUTE THIS SCRIPT:

You will need to install the PurdueShapes5GAN dataset before you can execute this script.
To that end, download the dataset archive

        datasets_for_AdversarialLearning.tar.gz

through the link "Download the image dataset for AdversarialLearning" provided at the top
of the HTML version of the main module doc page and store it in the 'Examples' directory
of the DLStudio distribution.  Subsequently, execute the following command in that
directory:

        tar zxvf datasets_for_AdversarialLearning.tar.gz

This command will create a 'dataGAN' subdirectory and deposit the following dataset archive
in that subdirectory:

        PurdueShapes5GAN-20000.tar.gz

Now execute the following in the "dataGAN" directory:

        tar zxvf PurdueShapes5GAN-20000.tar.gz

This is a dataset of 20,000 color images of size 64x64 that consist of randomly generated
patterns placed at random locations in the images and assigned randomly chosen colors.

To execute this script:

          python3 run_vae.py

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

epochs = 20                     ## for debugging
#epochs = 300

batch_size = 48         

learning_rate = 1e-4

image_size = (64,64)                
decoder_out_size = (64,64)



########################################################################
##  The following three choices involve paired selections:

##  Choice 1:
#encoder_out_size = (8,8)
#encoder_out_ch  = 512                     ##  when encoder_out_size = (8,8)

##  Choice 2:
encoder_out_size = (16,16)
encoder_out_ch  = 256                      ## when encoder_out_size = (16,16)

##  Choice 3:
#encoder_out_size = (32,32)
#encoder_out_ch  = 128                     ## when encoder_out_size = (32,32)
########################################################################


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
                       encoder_in_im_size = image_size,
                       encoder_out_im_size = encoder_out_size,
                       decoder_out_im_size = decoder_out_size,
                       encoder_out_ch = encoder_out_ch,
                       num_repeats = 1,
                       path_saved_encoder = "./saved_VAE_encoder_model",
                       path_saved_decoder = "./saved_VAE_decoder_model",
                    )
          

number_of_learnable_params_in_vae = sum(p.numel() for p in vae.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in VAE: %d" % number_of_learnable_params_in_vae)

vae.set_dataloader()

vae.run_code_for_training_VAE( vae, loss_weighting=0.1,  display_train_loss=True )    ## loss_weighting multiplies the KLD loss

vae.run_code_for_evaluating_VAE(vae, visualization_dir = "vae_visualization_dir")
