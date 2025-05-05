#!/usr/bin/env python

##  example_for_triplet_loss.py


"""
The goal of this script is to illustrate metric learning with the Triplet Loss.

Pay attention to the choice of the backbone model needed for generating the
embeddings in Lines (1) and (2) of the code below. Uncomment the one you want to
experiment with.  As shown, you can either choose ResNet-50 or the "homebrewed"
network defined in the MetricLearning class.

Also note the choice you need to make at the size of the embedding vectors.

When you choose the pre-trained ResNet-50 for the backbone, you should get about
84% for the "Precision@1" accuracy rate with TRIPLET LEARNING without any
hyperparameter tuning whatsoever.
"""

import random
import numpy
import torch
import os, sys

from DLStudio import *
from MetricLearning import *


seed = 0           
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
numpy.random.seed(seed)
torch.backends.cudnn.deterministic=True
torch.backends.cudnn.benchmarks=False
os.environ['PYTHONHASHSEED'] = str(seed)


##  watch -d -n 0.5 nvidia-smi
##  tensorboard --logdir tb_log_dir

trunk_model =  "RESNET50"                                                  ## (1)
#trunk_model =  "HOMEBREWED"                                               ## (2)


dls = DLStudio(
#                 dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
#                 dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/CIFAR-10/",
                  dataroot = "./data/CIFAR-10/",
                  image_size = [32,32],
                  path_saved_model = "./saved_model",
                  learning_rate = 1e-4,
                  epochs = 8,
                  batch_size = 160,
                  use_gpu = True,
              )

metric_learner = MetricLearning(
                      dlstudio = dls,
                      embedDim = 128,               ## size of the embedding vectors
                      trunk_model = trunk_model,
                 )

dls.load_cifar_10_dataset_with_augmentation()

metric_learner.run_code_for_training_with_triplet_loss()

metric_learner.visualize_clusters_with_tSNE("TRIPLET")

metric_learner.evaluate_metric_learning_performance("TRIPLET")
