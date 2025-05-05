#!/usr/bin/env python

##  playing_with_skip_connections.py

"""
This script illustrates how to actually use the inner class SkipConnections of
the DLStudio module.

As shown in the calls below, a CNN is constructed by calling on the constructor for
the BMEnet class.

You can easily create a CNN with arbitrary depth just by using the "depth"
constructor option for the BMEnet class.  BMEnet creates a network by using
multiple blocks of SkipBlock.
"""

import random
import numpy
import torch
import os, sys

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

dls = DLStudio(
#                  dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
                  dataroot = "./data/CIFAR-10/",
                  image_size = [32,32],
                  path_saved_model = "./saved_model",
                  momentum = 0.9,
                  learning_rate = 1e-4,
                  epochs = 6,
                  batch_size = 4,
                  classes = ('plane','car','bird','cat','deer','dog','frog','horse','ship','truck'),
                  use_gpu = True,
              )

bme_net = dls.BMEnet(dls, skip_connections=True, depth=8)         ## if you want to use skips
#bme_net = skip_con.BMEnet(skip_connections=False, depth=8)         ## if you don't want to use skips

bme_net.load_cifar_10_dataset()

## display network properties
number_of_learnable_params = sum(p.numel() for p in bme_net.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in the model: %d" % number_of_learnable_params)

## training and testing
bme_net.run_code_for_training(bme_net, display_images=False)

#import pymsgbox      
#response = pymsgbox.confirm("Finished training.  Start testing on unseen data?") 
#if response == "OK":   

bme_net.run_code_for_testing(bme_net, display_images=False)

