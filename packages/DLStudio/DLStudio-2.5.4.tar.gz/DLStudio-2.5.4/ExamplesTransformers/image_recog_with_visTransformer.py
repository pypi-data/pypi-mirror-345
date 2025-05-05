#!/usr/bin/env python

##  image_recog_with_visTransformer.py

"""
This script is for experimenting with visTransformer implementation in the Transformers
module in DLStudio.

See ny Week 14 slides at Purdue's Deep Learning class for further information regarding
this part of the Transformers module.
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
from Transformers import *
import os, sys


dataroot = "./data/CIFAR-10/"
#dataroot =  "/home/kak/ImageDatasets/CIFAR-10/"
#dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/CIFAR-10/"

embedding_size = 256

num_basic_encoders = 8
num_atten_heads = 4

epochs = 60

#batch_size = 8
batch_size = 48         

learning_rate = 1e-4

image_size = (32,32)                
patch_size = (8,8)                    

dls = DLStudio(
                  dataroot = dataroot,
                  image_size = image_size,
                  path_saved_model = "./saved_visTran_model",
                  learning_rate = learning_rate,        
                  epochs = epochs,
                  batch_size = batch_size,
                  classes = ('plane','car','bird','cat','deer','dog','frog','horse','ship','truck'),
                  use_gpu = True,
              )

vit = visTransformer( 
                  dl_studio = dls,
                  patch_size = patch_size,
                  embedding_size = embedding_size,
                  num_basic_encoders = num_basic_encoders,
                  num_atten_heads = num_atten_heads,
                  save_checkpoints = True,
                  checkpoint_freq = 10         ## a checkpoint will be created every so many epochs
      )


vit.load_cifar_10_dataset()

## display network properties
number_of_learnable_params_in_vit = sum(p.numel() for p in vit.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in visTransfomer: %d" % number_of_learnable_params_in_vit)

dls.load_cifar_10_dataset()

vit.run_code_for_training_visTransformer(dls, vit, display_train_loss=True, checkpoint_dir="checkpoints_visTrans")

vit.run_code_for_evaluating_visTransformer()





