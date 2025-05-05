# -*- coding: utf-8 -*-

__version__   = '2.5.4'
__author__    = "Avinash Kak (kak@purdue.edu)"
__date__      = '2025-May-4'                   
__url__       = 'https://engineering.purdue.edu/kak/distDLS/DLStudio-2.5.4.html'
__copyright__ = "(C) 2025 Avinash Kak. Python Software Foundation."


__doc__ = '''


  You are looking at the MetricLearning module file in the DLStudio platform.
  For the overall documentation on DLStudio, visit:

           https://engineering.purdue.edu/kak/distDLS/



INTRODUCTION TO METRIC LEARNING:

    The main idea of metric learning is to learn a mapping from the images to
    their embedding vector representations in such a way that the embeddings for
    what are supposed to be similar images are pulled together and those for
    dissimilar images are pulled as far apart as possible.  After such a mapping
    function is learned, you can take a query image (whose class label is not
    known), run it through the network to find its embedding vector, and,
    subsequently, assign to the query images the class label of the nearest
    training-image neighbor in the embedding space.  As explained in my Metric
    Learning lecture in the Deep Learning class at Purdue, this approach to
    classification is likely to work under data circumstances when the more neural
    network classifiers fail.

    Two commonly used loss functions for metric learning are Pairwise Contrastive
    Loss and Triplet Loss.  

    Pairwise Contrastive Loss is based on extracting all the Positive and the
    Negative Pairs of images form a batch.  For a Positive Pair, both the images
    in the pair must have the same label, and, for a Negative Pair, the two labels
    must be different.  A minimization of the Pairwise Contrastive Loss should
    decrease the distance between the embedding vectors for a Positive Pair and
    increase the distance between the embedding vectors for a Negative Pair.  If
    the two embeddings in a Negative Pair are already well separated, there would
    be no point to have them contribute to the loss calculation.  This is
    accomplished by incorporating the notion of a margin.  The idea is that we
    want to increase the distance between the two embeddings in a Negative Pair to
    the value specified by the Margin and no more. Should it be the case that two
    such embeddings are already separated by a distance greater than the Margin,
    we do not include such pairs in the loss calculation.

    Triplet Loss, on the other hand, starts with the notion of triplets (i,j,k) of
    the indices for triplets of images in a batch, with no two of the indices
    being the same. The image indexed by i is considered to be the Anchor in the
    triplet, the image indexed by j as Positive, and the one by k as the Negative.
    We also refer to such triplets with the notation (Anchor, Pos, Neg).  We again
    need the notion of a Margin. When we form the (Anchor, Pos, Neg) triplets from
    a batch, we focus on only those Neg images that are further away from the
    Anchor than the Pos image, but no farther than the (Anchor,Pos) distance plus
    the Margin.  Including the Negative images that are closer than the (Anchor,
    Pos) distance can make the learning unstable and including the Negatives that
    farther than the "(Anchor,Pos) plus the Margin" distance is likely to be
    wasteful.

    Forming set of Positive and Negative Pairs for the Pairwise Contrastive Loss
    and forming sets of Triplets for the Triplet Loss is referred to as Mining a
    batch.  This allows us to talk about concepts like "negative-hard mining",
    "negative semi-hard mining", etc., that depend on the relative distances
    between the images in the Negative Pairs and the distance of a negative
    vis-a-vis those in a Positive Pair.


    PROGRAMMING CHALLENGES:


    To calculate the Pairwise Contrastive Loss, you must be first extract Positive
    and Negative Pairs from a batch.  A Positive Pair means that both the
    embeddings in the pair carry the same class label and a Negative Pair means
    that the two embeddings in the pair have dissimilar labels.  From a
    programming standpoint, the challenge is how to form these pairs without
    scanning through a batch with 'for' loops --- since such loops are an anathema
    to any GPU based processing of data. What comes to our rescue are a
    combination of the broadcast properties of tensors (inherited from numpy) and
    tensor-based Boolean logic. For example, by comparing a column tensor of the
    sample labels in a batch with a row tensor of the same and testing for the
    equality of the sample labels, you instantly have a 2D array whose (i,j)
    element is True if the i-th and the j-th batch samples carry the same class
    label.

    Even after you have constructed the Positive and the Negative Pairs from a
    batch, your next mini-challenge is to reformat the batch sample indices in the
    pairs in order to conform to the input requirements of PyTorch's loss function
    torch.nn.CosineEmbeddingLoss.  The input consists of three tensors, the first
    two of which are of shape (N,M), where N is the total number of pairs
    extracted from the batch and M the size of the embedding vectors. The first
    such NxM tensor corresponds to the fist batch sample index in each pair. And
    the second such NxM tensor corresponds to the second batch sample index in
    each pair. The last tensor in the input args to the CosineEmbeddingLoss loss
    function is of shape Nx1, in which the individual values are either +1.0 or
    -1.0, depending on whether the pair formed by the first two embeddings is a
    Positive Pair or a Negative Pair.

    The programming challenge for calculating the Triplet Loss is similar to what
    it is for the Pairwise Contrastive Loss: How to extract all the triplets from
    a batch without using 'for' loops.  The first step is to form array index
    triplets (i,j,k) in which two indices are the same.  If B is the batch size,
    this is easily done by first forming a BxB array that is the logical negation
    of a Boolean array of the same size whose True values are only on the
    diagonal.  We can reshape this BxB Boolean array into three BxBxB shaped
    Boolean arrays, the first in which the True values exist only where i and j
    values are not the same, the second in which the True values occur only when i
    and k index values are not the same, and the third that has True values only
    when the j and k index values are not the same.  By taking a logial AND of all
    three BxBxB Boolean arrays, we get the result we want.  Next, we construct a
    BxBxB Boolean tensor in which the True values occur only where the first two
    index values imply that their corresponding labels are identical and where the
    last index corresponds to a label that does not agree with that for the first
    two index values.

    Even after you have formed the triplets, your next mini-challenge is to
    reformat the triplets into what you need to feed into the PyTorch loss
    function torch.nn.TripletMarginLoss. The loss function takes three arguments,
    each of shape (N,M) where N is the total number of triplets extracted from the
    batch and M the size of the embedding vectors.  The first such NxM tensor is
    the Anchor embedding vectors, the second for the Positive embedding vectors,
    the last for the Negative embedding vectors.


    EXAMPLE SCRIPTS:

    If you wish to use this module to learn about metric learning, your entry
    points should be the following scripts in the ExamplesMetricLearning directory
    of the distro:

        1.  example_for_pairwise_contrastive_loss.py

        2.  example_for_triplet_loss.py

    As the names imply, the first script demonstrates using the Pairwise
    Contrastive Loss for metric learning and the second script using the Triplet
    Loss for doing the same.  Both scripts can work with either the pre-trained
    ResNet-50 trunk model or the homebrewed network supplied with the
    MetricLearning module.


@endofdocs
'''


from DLStudio import DLStudio

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision                  
import torchvision.transforms as tvt
import torchvision.transforms.functional as tvtF
import torch.optim as optim

import faiss

import sys,os,os.path
import numpy as np
import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import glob                                                                                                           
import imageio                                                                                                        

from torchvision import models                      ## for resnet50
from matplotlib import cm
from sklearn.manifold import TSNE

from tensorboardX import SummaryWriter


## Suppress warnings, the first is presumably from all modules, and the second specific to
## matplotlib:
import warnings
warnings.filterwarnings("ignore")        
import logging
logging.getLogger('matplotlib').setLevel(level=logging.CRITICAL)

#______________________________  MetricLearning Class Definition  ________________________________

class MetricLearning(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''MetricLearning constructor can only be called with keyword arguments for the following
                      keywords: dlstudio, embedDim, trunk_model''')
        allowed_keys = 'dlstudio', 'embedDim', 'trunk_model'
        keywords_used = kwargs.keys()
        for keyword in keywords_used:
            if keyword not in allowed_keys:
                raise SyntaxError(keyword + ":  Wrong keyword used --- check spelling")  
        dlstudio = embedDim = None
        if 'dlstudio' in kwargs                      :   dlstudio  = kwargs.pop('dlstudio')
        if 'embedDim' in kwargs                      :   embedDim  = kwargs.pop('embedDim')
        if 'trunk_model' in kwargs                   :   trunk_model = kwargs.pop('trunk_model')
        if dlstudio:
            self.dlstudio = dlstudio
        if embedDim:
            self.embedDim = embedDim
        if trunk_model:
            self.trunk_model = trunk_model



    class EmbeddingGenerator1(nn.Module):
        """
        This network is from from Zhenye's GitHub page: https://github.com/Zhenye-Na/blog

        Class Path:  MetricLearning  ->  EmbeddingGenerator1
        """
        def __init__(self, metric_learner):
            super(MetricLearning.EmbeddingGenerator1, self).__init__()
            embedDim = metric_learner.embedDim
            self.conv_seqn = nn.Sequential(
                # Conv Layer block 1:
                nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                # Conv Layer block 2:
                nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout2d(p=0.05),
                # Conv Layer block 3:
                nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
                nn.BatchNorm2d(256),
                nn.ReLU(inplace=True),
                nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
            )
            self.fc_seqn = nn.Sequential(
                nn.Dropout(p=0.1),
                nn.Linear(4096, 1024),
                nn.ReLU(inplace=True),
                nn.Linear(1024, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(p=0.1),
                nn.Linear(512, embedDim)
            )

        def forward(self, x):
            x = self.conv_seqn(x)
            # flatten
            x = x.view(x.shape[0], -1)
            x = self.fc_seqn(x)
            return x



    class EmbeddingGenerator2(nn.Module):
        """
        This is the trunk model you get when you choose RESNET50 for the metric learning scripts 
        in the ExamplesMetricLearning directory.
        """
        def __init__(self, metric_learner):
            super(MetricLearning.EmbeddingGenerator2, self).__init__()
            embedDim = metric_learner.embedDim
            self.backbone = models.resnet50(pretrained=True)    ## Set to True if you want to use pretrained weights of ResNet 
                                                                ##   trained on the ImageNet dataset or else set to False 
                                                                ##   if you want to train from scratch
            num_ftrs = self.backbone.fc.in_features
            ##  Replace ResNet’s FC layer at the end with a Linear layer 
            ##    which will output embeddings of size embedDim:
            self.backbone.fc = nn.Linear(num_ftrs, embedDim)
#            print(self.backbone) # prints the model architecture

        def forward(self, x):
            x = self.backbone(x)
            return x


    ###%%%
    ####################################################################################################################
    ########################################   Metric Learning with Triplet Loss  ######################################

    def run_code_for_training_with_triplet_loss(self, display_images=False):        
        """
        For the Triplet Loss, you construct triplets of the samples in a batch in which the
        first two embeddings must carry the same class label and the label of the third
        embedding must not be same as for the other two.  Such a triplet is commonly
        denoted (Anchor, Pos, Neg).  That is, you treat the first element as the Anchor,
        the second as the Positive and the third as the Negative.  A triplet is formed
        only if the distance between the Anchor and the Neg is greater than the distance
        between the Anchor and the Pos.  We want all such Neg element to get farther away
        from the Anchor compared to how far the Pos element is --- but no farther than
        what's known as the Margin.  The idea is that if the Neg element is already beyond
        the Margin distance added to how far the Pos is, the Neg is already well separated
        from Pos and would not contribute to the learning process.

        The programming challenge for calculating the Triplet Loss is similar to what it
        is for the Pairwise Contrastive Loss: How to extract all the triplets from a batch
        without using 'for' loops.  The first step is to form array index triplets (i,j,k)
        in which two indices are the same.  If B is the batch size, this is easily done by
        first forming a BxB array that is the logical negation of a Boolean array of the
        same size whose True values are only on the diagonal.  We can reshape this BxB
        Boolean array into three BxBxB shaped Boolean arrays, the first in which the True
        values exist only where i and j values are not the same, the second in which the
        True values occur only when i and k index values are not the same, and the third
        that has True values only when the j and k index values are not the same.  By
        taking a logial AND of all three BxBxB Boolean arrays, we get the result we want.
        Next, we construct a BxBxB Boolean tensor in which the True values occur only
        where the first two index values imply that their corresponding labels are
        identical and where the last index corresponds to a label that does not agree with
        that for the first two index values.

        Even after you have formed the triplets, your next mini-challenge is to reformat
        the triplets into what you need to feed into the PyTorch loss function
        torch.nn.TripletMarginLoss. The loss function takes three arguments, each of shape
        (N,M) where N is the total number of triplets extracted from the batch and M the
        size of the embedding vectors.  The first such NxM tensor is the Anchor embedding
        vectors, the second for the Positive embedding vectors, the last for the Negative
        embedding vectors.
        """
        if os.path.exists("tb_log_dir"):   
            files = glob.glob("tb_log_dir" + "/*")
            for file in files:
                if os.path.isfile(file):
                    os.remove(file)
                else:
                    files = glob.glob(file + "/*")
                    list(map(lambda x: os.remove(x), files))
        else:
            os.mkdir("tb_log_dir")
        tb_writer = SummaryWriter("tb_log_dir")

        if self.trunk_model == "RESNET50":
            embedding_gen = self.EmbeddingGenerator2(self)
        elif self.trunk_model == "HOMEBREWED":
            embedding_gen = self.EmbeddingGenerator1(self)
        else:
            sys.exit("your choice for embedding generator is not legal")

        number_of_learnable_params = sum(p.numel() for p in embedding_gen.parameters() if p.requires_grad)  
        print("\n\nThe number of learnable parameters in the model: %d\n" % number_of_learnable_params)
        num_layers = len(list(embedding_gen.parameters()))     
        print("\nThe number of layers in the model: %d\n" % num_layers)   

        embedding_gen = embedding_gen.to(self.dlstudio.device)
        optimizer = optim.Adam(embedding_gen.parameters(), lr=self.dlstudio.learning_rate)
        triplet_loss_func  =  nn.TripletMarginLoss(margin=1.0)

        print("\n\nStarting training loop...")
        start_time = time.perf_counter()
        loss_tally = []
        elapsed_time = 0.0
        torch.set_printoptions(edgeitems=10_000, linewidth=120)
        for epoch in range(self.dlstudio.epochs):  
            print("")
            running_loss = 0.0
            for i, data in enumerate(self.dlstudio.train_data_loader):
                input_batch, labels = data
                input_batch = input_batch.to(self.dlstudio.device)
                labels = labels.to(self.dlstudio.device)
                ## Must zero out the gradients before calling the network for genering 
                ##  the embeddings:
                optimizer.zero_grad()
                embeddings_for_batch = embedding_gen(input_batch)   
                B = embeddings_for_batch.shape[0]                    ## embeddings_for_batch is of shape like (128,256) with the

                ##  Our next goal is to extract the triplets from the batch without using 'for' loops. For this I
                ##  will use a combination of array broadcasting properties of tensors and Boolean logic as suggested
                ##  by Tomek Korbak in ``Triplet loss and quadruplet loss via tensor masking".  As shown below, we 
                ##  start by constructing a Boolean tensor of shape BxBxB that contains True values only for the
                ##  index triples (i,j,k) for which no two indices are the same.  See my MetricLearning slides at DL for 
                ##  the associated explanation:
                not_equal_ij = ~ torch.eye(B,dtype=bool)
                i_not_equal_j = not_equal_ij.view(B,B,1)
                i_not_equal_k = not_equal_ij.view(B, 1, B)
                j_not_equal_k = not_equal_ij.view(1,B,B)
                ##  The BxBxB Boolean tensor shown below is not True at any element where any two of the three index values are
                ##  are the same:
                distinct_indices = i_not_equal_j  &  i_not_equal_k  & j_not_equal_k   
                distinct_indices = distinct_indices.to(self.dlstudio.device)
                ##  Next, we construct a BxBxB Boolean tensor in which the True values occur only where the first two index
                ##  values imply their that the corresponding labels are identical and where the last index corresponds to a
                ##  label that does not agree with that for the first two index values.
                labels_equal_ij = labels.view(1,B) == labels.view(B,1)
                labels_equal_ij = labels_equal_ij.to(self.dlstudio.device)
                labels_i_equal_j = labels_equal_ij.view(B,B,1)
                labels_i_equal_k = labels_equal_ij.view(B,1,B)
                valid_labels = labels_i_equal_j  &  ~ labels_i_equal_k
                valid_labels = valid_labels.to(self.dlstudio.device)                
                valid_labels_at_valid_indices = distinct_indices  &  valid_labels
                valids = torch.nonzero( valid_labels_at_valid_indices )
                ##  By default, the requires grad property of a new tensor is set to False.  We need to set 
                ##  it to True:
                anchor = embeddings_for_batch[valids[:,0]]
                anchor.requires_grad_()
                positive = embeddings_for_batch[valids[:,1]]
                positive.requires_grad_()
                negative = embeddings_for_batch[valids[:,2]]
                negative.requires_grad_()
                triplet_loss  =  triplet_loss_func( anchor, positive, negative )
                triplet_loss.backward() 
                running_loss += triplet_loss.item()
                how_many_triplets = anchor.shape[0]    
                if i % 20 == 19:
                    current_time = time.perf_counter()
                    elapsed_time = current_time - start_time 
                    avg_loss = running_loss / float(20)
                    loss_tally.append(avg_loss)
                    print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]  Number of Triplets: =%5d    Loss: %.3f" % 
                                                                   (epoch+1, self.dlstudio.epochs, i+1, elapsed_time, how_many_triplets, avg_loss))
                    tb_writer.add_scalar('Avg Loss', avg_loss, epoch+1)
                    running_loss = 0.0
                    if display_images:
                        logger = logging.getLogger()
                        old_level = logger.level
                        logger.setLevel(100)
                        plt.figure(figsize=[6,3])
                        plt.imshow(np.transpose(torchvision.utils.make_grid(inputs, 
                                                            normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                        plt.show()
                        logger.setLevel(old_level)
                optimizer.step()
        print("\nFinished Training\n")
        self.save_model(embedding_gen)
        plt.figure(figsize=(10,5))
        plt.title("Training Loss vs. Iterations for Triplet Learning")
        plt.plot(loss_tally)
        plt.xlabel("iterations")
        plt.ylabel("loss")
        plt.legend()
        plt.savefig("training_loss_vs_iters_for_TRIPLET_learning_and_trunk_model_" + self.trunk_model + "_with_" + str(self.dlstudio.epochs) + "_epochs.png")
        plt.show()



    ###%%%
    ####################################################################################################################
    ######################################   Metric Learning with Contrastive Loss  ####################################

    def run_code_for_training_with_contrastive_loss(self, display_images=False):        
        """
        To calculate the Pairwise Contrastive Loss, you must be first extract Positive and
        Negative Pairs from a batch.  A Positive Pair means that both the embeddings in
        the pair carry the same class label and a Negative Pair means that the two
        embeddings in the pair have dissimilar labels.  From a programming standpoint, the
        challenge is how to form these pairs without scanning through a batch with 'for'
        loops --- since such loops are an anathema to any GPU based processing of
        data. What comes to our rescue are a combination of the broadcast properties of
        tensors (inherited from numpy) and tensor-based Boolean logic. For example, by
        comparing a column tensor of the sample labels in a batch with a row tensor of the
        same and testing for the equality of the sample labels, you instantly have a 2D
        array whose (i,j) element is True if the i-th and the j-th batch samples carry the
        same class label.

        Even after you have constructed the Positive and the Negative Pairs from a batch,
        your next mini-challenge is to reformat the batch sample indices in the pairs in
        order to conform to the input requirements of PyTorch's loss function
        torch.nn.CosineEmbeddingLoss.  The input consists of three tensors, the first two
        of which are of shape (N,M), where N is the total number of pairs extracted from
        the batch and M the size of the embedding vectors. The first such NxM tensor
        corresponds to the fist batch sample index in each pair. And the second such NxM
        tensor corresponds to the second batch sample index in each pair. The last tensor
        in the input args to the CosineEmbeddingLoss loss function is of shape Nx1, in
        which the individual values are either +1.0 or -1.0, depending on whether the pair
        formed by the first two embeddings is a Positive Pair or a Negative Pair.
        """
        if os.path.exists("tb_log_dir"):   
            files = glob.glob("tb_log_dir" + "/*")
            for file in files:
                if os.path.isfile(file):
                    os.remove(file)
                else:
                    files = glob.glob(file + "/*")
                    list(map(lambda x: os.remove(x), files))
        else:
            os.mkdir("tb_log_dir")
        tb_writer = SummaryWriter("tb_log_dir")

        if self.trunk_model == "RESNET50":
            embedding_gen = self.EmbeddingGenerator2(self)
        elif self.trunk_model == "HOMEBREWED":
            embedding_gen = self.EmbeddingGenerator1(self)
        else:
            sys.exit("your choice for embedding generator is not legal")

        number_of_learnable_params = sum(p.numel() for p in embedding_gen.parameters() if p.requires_grad)  
        print("\n\nThe number of learnable parameters in the model: %d\n" % number_of_learnable_params)
        num_layers = len(list(embedding_gen.parameters()))     
        print("\nThe number of layers in the model: %d\n" % num_layers)   

        embedding_gen = embedding_gen.to(self.dlstudio.device)
        embedding_gen.train()                       ## put the network in the "train" mode as opposed to "eval" mode
        optimizer = optim.Adam(embedding_gen.parameters(), lr=self.dlstudio.learning_rate)
        contrastive_loss_func  =  nn.CosineEmbeddingLoss(margin=0.0)
        print("\n\nStarting training loop...")
        start_time = time.perf_counter()
        loss_tally = []
        elapsed_time = 0.0
        for epoch in range(self.dlstudio.epochs):  
            print("")
            running_loss = 0.0
            for i, data in enumerate(self.dlstudio.train_data_loader):
                input_batch, labels = data
                input_batch = input_batch.to(self.dlstudio.device)
                labels = labels.to(self.dlstudio.device)
                ## Must zero out the gradients before calling the network for genering 
                ##  the embeddings:
                optimizer.zero_grad()
                embeddings_for_batch = embedding_gen(input_batch)   
                ##  For convenience, define B and M
                B = embeddings_for_batch.shape[0]                    ## embeddings_for_batch is of shape like (128,256)
                M = embeddings_for_batch.shape[1]                    ## embedding vector size
                ##  Our next job is to construct a Boolean tensor of shape BxB that contains True values only for the
                ##  index pairs (i,j) for which the two indices are not the same.  See my MetricLearning slides at DL for 
                ##  the associated explanation:
                labels_equal = labels.view(1, B) == labels.view(B, 1)     ## Each entry in the BxB array is either True or False
                                                                          ## If the (i,j) entry is true, then i and j have same label
                labels_equal =  labels_equal & ~ torch.eye(B, dtype=bool).to(self.dlstudio.device)  ## Delete the diagonal entries 
                ## We flatten the BxB bool array into a B^2 dimensional flat tensor for the 3rd
                ## arg to the contrastive loss fumction:
                labels_equal_flattened = labels_equal.view(-1)
                Y = labels_equal_flattened.int()
                Y[Y==0] = -1.0
                how_many_pos = torch.count_nonzero( Y[Y==1] ).item()
                how_many_neg = torch.count_nonzero( Y[Y==-1] ).item()
                X1 = torch.repeat_interleave( embeddings_for_batch, B, dim=0)
                X2 = torch.tile(embeddings_for_batch, (B,1))           
                loss = contrastive_loss_func(X1, X2, Y)
                loss.backward() 
                running_loss += loss.item()
                if i % 20 == 19:
                    current_time = time.perf_counter()
                    elapsed_time = current_time - start_time 
                    avg_loss = running_loss / float(20)
                    loss_tally.append(avg_loss)
                    print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]  [pos_pairs: %d   neg_pairs: %d]   Loss: %.3f" % 
                                                (epoch+1, self.dlstudio.epochs, i+1, elapsed_time, how_many_pos, how_many_neg, avg_loss))    
                    running_loss = 0.0
                    if display_images:
                        logger = logging.getLogger()
                        old_level = logger.level
                        logger.setLevel(100)
                        plt.figure(figsize=[6,3])
                        plt.imshow(np.transpose(torchvision.utils.make_grid(inputs, 
                                                            normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                        plt.show()
                        logger.setLevel(old_level)
                optimizer.step()
        print("\nFinished Training\n")
        self.save_model(embedding_gen)
        plt.figure(figsize=(10,5))
        plt.title("Training Loss vs. Iterations for Constrastive Learning")
        plt.plot(loss_tally)
        plt.xlabel("iterations")
        plt.ylabel("loss")
        plt.legend()
        plt.savefig("training_loss_vs_iters_for_CONTRASTIVE_learning_and_trunk_model_" + self.trunk_model + "_with_" + str(self.dlstudio.epochs) + "_epochs.png")
        plt.show()


    ###%%%
    ####################################################################################################################
    ########################################   Visualization and Evaluation Code  ######################################

    def evaluate_metric_learning_performance(self, mode=""):
        """
        The arg "mode" is used for making more informative the output that is printed out.
        """
        if self.trunk_model == "RESNET50":
            embedding_gen = self.EmbeddingGenerator2(self)
        elif self.trunk_model == "HOMEBREWED":
            embedding_gen = self.EmbeddingGenerator1(self)
        else:
            sys.exit("your choice for embedding generator is not legal")
        
        embedding_gen.load_state_dict(torch.load(self.dlstudio.path_saved_model))
        embedding_gen.eval() 
        embedding_gen = embedding_gen.to(self.dlstudio.device)

        ##  Next, we generate the data for performance evaluation.  It consists of two parts: We randomly extract 
        ##  from the original training dataset 1000 or so images, pass them through the trained embedding generator,
        ##  and use these embedding vector to populate a vector space whose dimensionality is, naturally, that
        ##  of the embedding vectors.  At the same time, we also extract 1000 or so images from the test dataset.
        ##  These images are also passed through the same embedding generator.  Performance evaluation consists
        ##  of finding the nearest neighbor of each test-image embedding vector in the space spanned by the
        ##  training-image embedding vectors.  If the label of the nearest neighbor matches that of the test 
        ##  image, that contributes a unit to the "Precision @ rank 1" count.
        train_embeddings = np.empty((0,self.embedDim), dtype=float)      ## emdedDim = size of embedding vectors
        train_labels = np.empty(0, dtype=float)
        iterator = iter(self.dlstudio.train_data_loader)
        for i in range(len(self.dlstudio.train_data_loader)):    
            ##  Use 4 randomly selected batches for the training part of evaluation
            ##  IMPORTANT: these images are from the TRAINING part of the original image dataset
            if i > 3: break                  
            images, labels = next(iterator)
            images = images.to(self.dlstudio.device)
            embeddings = embedding_gen(images)
            train_embeddings = np.concatenate( (train_embeddings, embeddings.detach().cpu().numpy()), axis=0)
            train_labels = np.concatenate( (train_labels, labels), axis=0 )
        test_embeddings = np.empty((0,self.embedDim), dtype=float)
        test_labels = np.empty(0, dtype=float)
        iterator = iter(self.dlstudio.test_data_loader)
        for i in range(len(self.dlstudio.test_data_loader)):   
            ## Use 4 randomly selected batches for testing part of evaluation
            ##  IMPORTANT: these images are from the TESTING part of the original image dataset
            if i > 3: break                  
            images, labels = next(iterator)
            images = images.to(self.dlstudio.device)
            embeddings = embedding_gen(images)
            test_embeddings = np.concatenate( (test_embeddings, embeddings.detach().cpu().numpy()), axis=0)
            test_labels = np.concatenate( (test_labels, labels), axis=0 )
        index = faiss.IndexFlatL2(self.embedDim)                                ## create the indexer
#        print(index.is_trained)
        index.add(train_embeddings)
        ##  We want to see 3 nearest neighbors.  Ordinarily, if you are only calculated "Precision @ rank 1",
        ##  you'll only need to set "k = 1".  
        k = 3                          
        ##  If Q is the number of embeddings in test_embeddings, the following search will return
        ##  for I an array of shape (Q, k) with each row in this array a list of integer indexes 
        ##  to the vectors that are k closest neighbors of the query vector that corresponds to 
        ##  that row
        D, I = index.search(test_embeddings, k)  
        precision_at_rank_1 = 0        
        for j in range(len(test_labels)):
            nearest_vecs = I[j]
            ##  We only retain the first element "nearest_vecs[0]" for "Precition @ 1" evaluation:
            if test_labels[j] == train_labels[ nearest_vecs[0] ]:
                precision_at_rank_1 += 1
        precision_at_rank_1_precent =  (precision_at_rank_1 / float(len(test_labels))) * 100
        print("\n\n\n\nprecision_at_rank_1 with " + mode + " learning: ", precision_at_rank_1_precent)
        print("\n\n")
        print("""The accuracy result shown above was produced with no
hyperparameter tuning of the network.  In particular, it is
based on using the default values for the margins for the
loss functions, which is probably the worst thing do to in
metric learning.\n\n""")



    def visualize_clusters_with_tSNE(self, mode=""):
        """
        The arg "mode" is used for making more informative the name of the hardcopy figure that is saved.

        For an explanation of the t-SNE visualization algorithm, see the Slides 78 through 95 of my "Metric Learning" 
        lecture slides in the syllabus for the DL class.
        """
        class_labels = {0:'airplane', 1:'automobile', 2:'bird', 3:'cat', 4:'deer', 5:'dog', 6:'frog', 7:'horse', 8:'ship', 9:'truck'}

        if self.trunk_model == "RESNET50":
            embedding_gen = self.EmbeddingGenerator2(self)
        elif self.trunk_model == "HOMEBREWED":
            embedding_gen = self.EmbeddingGenerator1(self)
        else:
            sys.exit("your choice for embedding generator is not legal")

        embedding_gen = embedding_gen.to(self.dlstudio.device)
        embedding_gen.load_state_dict(torch.load(self.dlstudio.path_saved_model))
        embedding_gen.eval() 
        ##  Generate the data for visualization.  We will use three randomly selected batches worth of embeddings.  We need those 
        ##  embeddings and the true labels of the corresonding images:
        vis_embeddings = np.empty((0,self.embedDim), dtype=float)
        vis_labels = np.empty(0, dtype=float)
        iterator = iter(self.dlstudio.train_data_loader)
        for i in range(len(self.dlstudio.train_data_loader)):
            ## Use 4 randomly selected batches for visualization:
            if i > 3: break                  
            images, labels = next(iterator)
            images = images.to(self.dlstudio.device)
            embeddings = embedding_gen(images)
            vis_embeddings = np.concatenate( (vis_embeddings, embeddings.detach().cpu().numpy()), axis=0)
            vis_labels = np.concatenate( (vis_labels, labels), axis=0 )
        ##  The first arg sets the dimensionality of the visualization space.  For the other args to tSNE 
        ##  see my explanation on tSNE in the slides on Metric Learning in my DL class:
        tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=1000)
        ##  Visualization projections:
        tsne_proj = tsne.fit_transform( torch.tensor(vis_embeddings) ) 
        # Plotting embeddings using matplotlib
        color_list = cm.get_cmap('tab10').colors
        fig, ax = plt.subplots(figsize=(8,8))
        num_categories = 10 # 10 for MNIST, CIFAR-10
        for lab in range(num_categories):
            indices = vis_labels == lab
            ax.scatter(tsne_proj[indices,0],tsne_proj[indices,1], c=color_list[lab], label = class_labels[lab])
            ax.legend(fontsize='large', markerscale=2)
            ax.legend(bbox_to_anchor=(1.06, 1), loc='upper right')          ## To move the legend outside the cluster display box
        if mode is not None:
            plt.title("Metric Learning with " + mode + " Loss_" + "and_" + str(self.dlstudio.epochs) + "_epochs")
            plt.savefig("tSNE_clustering_with_trunk_model_" + self.trunk_model + "_and_" + mode + "_loss" + "_for_" + str(self.dlstudio.epochs) + "_epochs.png")
        plt.show()


    def save_model(self, model):
        '''
        Save the trained model to a disk file
        '''
        torch.save(model.state_dict(), self.dlstudio.path_saved_model)


#_________________________  End of MetricLearning Class Definition ___________________________

#______________________________    Test code follows    _________________________________

if __name__ == '__main__': 
    pass
