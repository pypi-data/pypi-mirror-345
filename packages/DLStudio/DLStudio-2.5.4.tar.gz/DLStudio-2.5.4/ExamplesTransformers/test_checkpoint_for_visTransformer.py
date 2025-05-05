#!/usr/bin/env python

##  test_checkpoint_for_visTransformer.py

"""
    This script is for experimenting with the checkpoints that are created during the
    training of visTransformer.

    For an introduction to the idea of transformers, read the large comment block associated
    at the beginning of this block

    Calling syntax:

         python3  test_checkpoint_for_visTransformer.py  checkpoints_visTrans  N                  ## (A)

    where N is index for the checkpoint.  For example, if your training code ran for 40
    epochs, the checkpoints would be named:

                  checkpoint_0_for_epoch_10          ## for the main visTransformer model
                  checkpoint_1_for_epoch_10          ## for PatchEmbeddingGenerator

                  checkpoint_0_for_epoch_20          ## for the main visTransformer model
                  checkpoint_1_for_epoch_20          ## for PatchEmbeddingGenerator

                  checkpoint_0_for_epoch_30          ## for the main visTransformer model
                  checkpoint_1_for_epoch_40          ## for PatchEmbeddingGenerator
    
                  ...
                  ...

    In the call at Line (A) above, you would set N to 10 for the first checkpoint, to 20 
    for the second checkpoint, to 30 for the third checkpoint, and so on.

"""


from DLStudio import *
from Transformers import *
import os, sys

dataroot = "./data/CIFAR-10/"
#dataroot =  "/home/kak/ImageDatasets/CIFAR-10/"
#dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/CIFAR-10/"

embedding_size = 128

num_basic_encoders = 4
num_atten_heads = 4

#batch_size = 12
batch_size = 64       

image_size = (32,32)               ## need to be consistent with the values used for training
patch_size = (8,8)                 ## need to be consistent with the values used for training


dls = DLStudio(
                  dataroot = dataroot,
                  image_size = image_size,
                  path_saved_model = "./saved_visTran_model",
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
      )

## display network properties
number_of_learnable_params_in_vit = sum(p.numel() for p in vit.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in visTransfomer: %d" % number_of_learnable_params_in_vit)

vit.load_cifar_10_dataset()

vit.run_code_for_evaluating_checkpoint(vit, "checkpoints_visTrans")


