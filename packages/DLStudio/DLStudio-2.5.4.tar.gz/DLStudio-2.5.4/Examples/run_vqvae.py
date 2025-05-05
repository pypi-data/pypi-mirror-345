#!/usr/bin/env python

##  run_vqvae.py

"""
This script is for experimenting with the VQVAE (Vector Quantized VAE) inner class in
the main DLStudio class of the DLStudio platform.

The VQVAE class is derived from the Autoencoder class.  

The heavy lifting in VQVAE is done by the two Vector Quantizer classes that I have
borrowed from the "zalandoresearch" user at GitHub:

             https://github.com/zalandoresearch/pytorch-vq-vae    

Vector quantization is basic to Codebook learning which is based on the assumption
that each image in your dataset can be represented by a fixed number of embedding
vectors of a prescribed dimensionality.  The learned Codebook is best thought of as a
fixed-sized vocabulary for representing the images.

For the Encoder and the Decoder, the demonstration in the VQVAE class uses the
implementations defined for the parent class Autoencoder.



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

                 python3 run_vqvae.py

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



epochs = 2          ## for debugging
#epochs = 300

batch_size = 48      ## for debugging   
#batch_size = 128

learning_rate = 1e-4

## The dataset images:
image_size = (64,64)                


## Specifying the size of the images reconstructed by the Decoder:
decoder_out_size = (64,64)



########################################################################
##  The following three Choices are combined selections:

##  Choice 1:
## encoder_out_size = (8,8)
## encoder_out_ch  = 512                     ##  when encoder_out_size = (8,8)
## codebook_vec_dim  = 512                   ##  Must be the same as "encoder_out_ch"

##  Choice 2:
encoder_out_size = (16,16)
encoder_out_ch  = 256                        ## when encoder_out_size = (16,16)
codebook_vec_dim  = 256                      ##  Must be the same as "encoder_out_ch"

##  Choice 3:
#encoder_out_size = (32,32)
#encoder_out_ch  = 128                       ## when encoder_out_size = (32,32)
#codebook_vec_dim  = 128                     ##  Must be the same as "encoder_out_ch"
########################################################################



## Specifying the Codebook:
num_codebook_vecs = 512       ##  For the number of embedding vectors in the Codebook.  The Codebook
                              ##     constitutes a finite vocabulary for representing the training images.

## For calculating the vector-quantization losses:
commitment_cost = 0.25
decay = 0.99

dls = DLStudio(
                  dataroot = dataroot,
                  image_size = image_size,
                  learning_rate = learning_rate,        
                  epochs = epochs,
                  batch_size = batch_size,
                  use_gpu = True,
              )


vqvae  =  DLStudio.VQVAE( 
                       dl_studio = dls,
                       encoder_in_im_size = image_size,
                       encoder_out_im_size = encoder_out_size,
                       decoder_out_im_size = decoder_out_size,
                       encoder_out_ch = encoder_out_ch,
                       num_repeats = 1,
                       num_codebook_vecs = num_codebook_vecs,
                       codebook_vec_dim = codebook_vec_dim, 
                       commitment_cost = commitment_cost, 
                       decay = decay,
                       path_saved_encoder = "./saved_VQVAE_encoder_model",
                       path_saved_decoder = "./saved_VQVAE_decoder_model",
                       path_saved_vector_quantizer = "./saved_VQVAE_vector_quantizer_model",
                    )
          

number_of_learnable_params_in_vqvae = sum(p.numel() for p in vqvae.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in VAE: %d" % number_of_learnable_params_in_vqvae)

vqvae.set_dataloader()

vqvae.run_code_for_training_VQVAE( vqvae, display_train_loss=True )   

vqvae.run_code_for_evaluating_VQVAE(vqvae, visualization_dir = "vqvae_visualization_dir")
