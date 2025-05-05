#!/usr/bin/env python

##  run_autoencoder.py

"""
The purpose of this script is to experiment with the Autoencoder class that is an inner class
of the main DLStudio class.

Please keep in mind that I wrote the Autoencoder class to serve as a base class for the VAE
class.  It is the Autoencoder that defines the main Encoder and the Decoder that are subsequently
used in the VAE class.  Subsequently, VAE extends the logic of Autoencoder's Encoder with the 
logic that is specific to variational encoding.

If you execute this script with a sufficiently high value for the number of epochs, the output 
images produced by the Decoder will be virtually identical to those at the input to the 
Encoder.  The reason for that is not too difficult to understand:  The Encoder progressively 
reduces the size of the image while throwing information related to inter-pixel relationships
into the channel dimension.  So, one could argue that with sufficient training (and in the
absence of overfitting), we can expect minimal information loss between the input to the
Encoder and its output.  Subsequently, if the Decoder were to "expand" the output of the
Encoder back into an image of the same size and shape as the input, it is likely that the
final output will be very similar to the input.


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

          python3 run_autoencoder.py

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


#epochs = 20                    ##  for debugging
epochs = 200 

batch_size = 48         

learning_rate = 1e-4

image_size = (64,64)                
decoder_out_size = (64,64)



#######################################################################
##  The following three choices involve are paired selections:

##  Choice 1:
#encoder_out_size = (8,8)
#encoder_out_ch  = 512                     ## when encoder_out_size = (8,8)

##  Choice 2:
encoder_out_size = (16,16)
encoder_out_ch  = 256                      ## when encoder_out_size = (16,16)

##  Choice 3:
#encoder_out_size = (32,32)
#encoder_out_ch  = 128                     ## when encoder_out_size = (32,32)
#######################################################################



dls = DLStudio(
                  dataroot = dataroot,
                  image_size = image_size,
                  learning_rate = learning_rate,        
                  epochs = epochs,
                  batch_size = batch_size,
                  use_gpu = True,
              )


autoenc  =  DLStudio.Autoencoder( 
                         dl_studio = dls,
                         encoder_in_im_size = image_size,
                         encoder_out_im_size = encoder_out_size,
                         decoder_out_im_size = decoder_out_size,
                         encoder_out_ch = encoder_out_ch,
                         num_repeats = 1,
                         path_saved_model = "./saved_autoencoder_model",
                       )
          

number_of_learnable_params_in_autoencoder = sum(p.numel() for p in autoenc.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in the autoencoder: %d" % number_of_learnable_params_in_autoencoder)

autoenc.set_dataloader()

autoenc.run_code_for_training_autoencoder( display_train_loss=True )

autoenc.run_code_for_evaluating_autoencoder(visualization_dir = "autoencoder_visualization_dir")
