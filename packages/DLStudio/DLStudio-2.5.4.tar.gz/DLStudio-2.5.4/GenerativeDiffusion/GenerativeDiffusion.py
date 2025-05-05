# -*- coding: utf-8 -*-

__version__   = '2.5.4'
__author__    = "Avinash Kak (kak@purdue.edu)"
__date__      = '2025-May-4'                   
__url__       = 'https://engineering.purdue.edu/kak/distDLS/DLStudio-2.5.4.html'
__copyright__ = "(C) 2025 Avinash Kak. Python Software Foundation."


__doc__  =  '''

You are looking at the GenerativeDiffusion module file in the DLStudio platform.
For the overall documentation on DLStudio, visit:

           https://engineering.purdue.edu/kak/distDLS/


                         ************************


REGARDING THE ORIGIN OF THE CODE IN THIS FILE:


Most of the code you see in this file was drawn from the sources at the GitHub
project "Improved Diffusion" at

         https://github.com/openai/improved-diffusion

The source code at the above website is the implementation for the work described
in the paper "Improved Denoising Diffusion Probabilistic Models" by Nichol and
Dhariwal that you can download from:

         https://arxiv.org/pdf/2102.09672.pdf

That GitHub code library consists of roughly 3900 lines of Python distributed over
10 files in three different directories.  The code you'll see here contains around
750 lines of that code and that too after several changes to simplify the
organization of the code and to also simplify the call syntax for many of the
functions.

As just one example of my simplification of code organization, the original code
library at GitHub uses the GaussianDiffusion class through a subclass named
SpacedDiffusion that is defined in a utility file called script_util.py.  I got
rid of the SpacedDiffusion class and incorporated that functionality in a rather
small function inside the GaussianDiffusion class.  Along the same lines, I also
either eliminated some of the UNetModel's functionality that existed in the form
of method definitions or incorporated those methods in the class definition for
UNetModel.

Another change I made to the UNetModel class was to make the use of "attention" an
option in the constructor call for UNetModel.  I did so because attention does not
seem to matter if you are using diffusion based modeling for, say, 64x64 images
--- or, for that matter, even larger images from the CelebA dataset as long as you
resize them to 64x64.

Obviously, the GitHub code library is much more general and will allow you to do
the kinds of experiments (such as conditional diffusion) that my smaller version
of the code base will not.

In presenting the code you see here, my main goal is to be able to teach
efficiently the core ideas of diffusion based modeling of data.  My hope is that
after the students have understood the core ideas, they can always go to the
original code base at GitHub for more sophisticated experiments.



                         ************************


INTRODUCTION TO GENERATIVE DIFFUSION FOR DATA MODELING:


This module in DLStudio addresses the other approach to generative data modeling
--- the one based on what's known as "Denoising Diffusion".  As explained in my
Week 11 slides, the idea is to have two Markov processes, with one that subjects a
training image incrementally to diffusing Markov transitions until it becomes pure
noise, and the other that starts with Gaussian isotropic noise and denoises it
incrementally until what emerges is an image that looks like those in your
training data.

We denote the two Markov chains as the p-chain and the q-chain, with the former
standing for progressively denoising isotropic Gaussian noise until an image
emerges, and the latter for a progressive applications of diffusion to an image
from the training dataset until it turns into noise.

It is important to memorize what the names "p-chain" and "q-chain" stand for since
the same notion is used in the code.  Again, "p" stands for denoising and "q"
stands for diffusion.

Another thing you want to commit to memory is that temporal progression means two
different things in the two chains.  Let's say you have chosen T for the number of
timesteps in the two chains.  If you assume that the timesteps progress from 0 to
T in the forward q-chain, then you must also assume that the timesteps progress
from T to 0 in the reverse p-chain. What that implies is that a one-step
transition in the q-chain means going from timestep t-1 to t.  On the other hand,
the corresponding timestep transition in the p-chain PROGRESSES from t to t-1.

Let's now talk about the nature of the noise we are going to use in our framework.
In principle, the noise that you start with for the purpose of its transformation
into a recognizable image can be from any probability distribution. However, in
practice, you are likely to use isotropic Gaussian noise because of its unique
property that multiple consecutive transitions in a Markov chain can be combined
into a single calculation.

The above observation plays a central role if how you create a software
implementation for generative data modeling with diffusion.  Each training cycle
starts with acquiring a fresh image from the training dataset, randomly choosing a
timestep t in the forward q-chain, and, through a single calculation, estimating
the q-chain transition probability q(x_t | x_0).  This calculation is based on the
formula given by Eq. (67) of my Week 11 slides.  Up to this point there is no
learning involved and that's because there are no learnable parameters in the
forward q-chain.  

While the amount of noise that is injected into the data at each transition in the
forward q-chain is set by the user, how much denoising to carry out at the
corresponding transition in the reverse p-chain is determined by a neural network
whose job is to estimate the amount of denoising that, in a sense, would be
"exact" opposite of the extent of diffusion carried at the corresponding
transition in the forward q-chain.

Here is a summary of how to train the neural network mentioned above:

    --- At each iteration of training the neural network, randomly choose a
        timestep t from the range that consists of T timesteps.

    --- Apply a single cumulative q-chain transition to the input training image
        that would be equivalent to taking the input image through t consecutive
        transitions in the q-chain.

    --- For each q-chain transition to the timestep t, use the Bayes' Rule to
        estimate the posterior probability q( x_{t-1} | x_t, x_0 ) from the Markov
        transition probability q( x_t | x0, x_{t-1} ).

    --- Use the posterior probabilities mentioned above as the target for training
        the neural network whose job is to estimate the transition probability
        p( x_{t-1} | x_t ) in the reverse p-chain.  The loss function for training
        the neural network could be the KL-Divergence between the posterior
        q( x_{t-1} | x_t, x_0 ) and the predicted p( x_{t-1} | x_t ).

        Another possibility for the loss would be the MSE error between the
        isotropic noise that was injected in the q-chain transition in question
        and the prediction of the same in the p-chain by using the posterior
        estimates for the mean and the variance using the transition probability
        p( x_{t-1} | x_t ) that you get from the neural network.

        Yet another possibility is to directly form an estimate for the input
        image x_0 using the above-mentioned posterior estimates for the mean and
        the variance and then construct an MSE loss based on the difference
        between the estimated x_0 and its true value.
        
As should be clear from the above description, the sole goal of training the
neural network is to make it an expert at the prediction of the denoising
transition probabilities p( x_{t-1} | x_t ).  Typically, you carry out the
training in an infinite loop while spiting out the checkpoints every so often.

When you are ready to see the image generation power of a checkpoint, you start
with isotropic Gaussian noise as the input and take it through all of the T
timestep p-chain transitions that should lead to a recognizable image.


                         **************************


The ExamplesDiffusion Directory:

You will find the following scripts in the directory ExamplesDiffusion:

    0.   README

    1.   RunCodeForDiffusion.py

    2.   GenerateNewImageSamples.py

    3.   VisualizeSamples.py

As explained in the README, you will need all three Python scripts listed above to
do any experiments with diffusion in DLStudio.  Of these, the first,
RunCodeForDiffusion.py, is for training the neural network to become an expert in
estimating the p-chain transition probabilities

                 p( x     |  x  )
                     t-1      t            

The timestamp subscripts on the data x in this transition probability may look a
bit strange to those who are not familiar with the notion of the reverse Markov
chain called p-chain in diffusion modeling.  In a reverse Markov chain, the time
PROGRESSES from some user-specified T to 0.  Therefore, the timestamp t-1 comes
AFTER the timestamp t.

To run the training code on your image dataset, you will have to point the
"data_dir" constructor option of the GenerativeDiffusion class in the script
RunCodeForDiffusion.py to your dataset directory.  Depending on your training
dataset, you may also have to set some of the other constructor parameters in the
script RunCodeForDiffusion.py.  For example, if the image size in your dataset is
different from 64x64, you will have to supply the image_size parameter for the
GenerativeDiffusion class.

After the model has been trained, you must call the script
GenerateNewImageSamples.py to generate new image samples from the learned model.
These images are placed in a numpy ndarray archive.  Finally, you must call the
script VisualizeSamples.py to create the individual images from the numpy archive.

Please make sure to go through the README in the ExamplesDiffusion directory
before you start playing with the code in this file.

@endofdocs
'''

import sys,os,os.path
import math
import random
import matplotlib.pyplot as plt
import time
import glob 
import copy
import enum

import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
import torchvision                  


###########################################################################################################################
#############################################   Start of GenerativeDiffusion  #############################################

class GenerativeDiffusion(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''GenerativeDiffusion constructor can only be called with keyword arguments for the following
                      keywords: epochs, lr, learning_rate, batch_size, momentum, image_size, data_dir, dataroot, path_saved_model, 
                      use_gpu, ngpu, dlstudio, num_channels, device, log_interval, save_interval, ema_rate, diffusion, network''')
        allowed_keys = 'dataroot','data_dir','num_channels', 'lr', 'image_size','path_saved_model','momentum','learning_rate','epochs','batch_size', \
                       'classes','use_gpu','ngpu','dlstudio','log_interval','save_interval','ema_rate','diffusion','network','clip_denoised','num_samples',\
                       'batch_size_image_generation','gen_new_images'
        keywords_used = kwargs.keys()                                                                 
        for keyword in keywords_used:                                                                 
            if keyword not in allowed_keys:                                                           
                raise SyntaxError(keyword + ":  Wrong keyword used --- check spelling")  
        learning_rate = epochs = batch_size = convo_layers_config = momentum = gen_new_images = None
        image_size = fc_layers_config = lr = data_dir = num_channels = lr = dataroot =  path_saved_model = classes = use_gpu = None
        latent_vector_size = ngpu = save_interval = log_interval = clipping_threshold = clip_denoised = num_samples = batch_size_image_generation =  None
        if 'data_dir' in kwargs                      :   data_dir = kwargs.pop('data_dir')
        if 'num_channels' in kwargs                  :   num_channels = kwargs.pop('num_channels')
        if 'lr' in kwargs                            :   lr = kwargs.pop('lr')
        if 'batch_size' in kwargs                    :   batch_size = kwargs.pop('batch_size')
        if 'image_size' in kwargs                    :   image_size = kwargs.pop('image_size')

        if 'log_interval' in kwargs                  :   log_interval = kwargs.pop('log_interval')
        if 'save_interval' in kwargs                 :   save_interval = kwargs.pop('save_interval')
        if 'ema_rate' in kwargs                      :   ema_rate = kwargs.pop('ema_rate')
        if 'diffusion' in kwargs                     :   diffusion = kwargs.pop('diffusion')
        if 'network' in kwargs                       :   network = kwargs.pop('network')
        if 'gen_new_images' in kwargs                :   gen_new_images = kwargs.pop('gen_new_images')

        if 'ngpu' in kwargs                          :   ngpu  = kwargs.pop('ngpu')           
        if 'path_saved_model'in kwargs               :   path_saved_model = kwargs.pop('path_saved_model')

        if 'clip_denoised' in kwargs                 :   clip_denoised  = kwargs.pop('clip_denoised')
        if 'num_samples' in kwargs                   :   num_samples  = kwargs.pop('num_samples')
        if 'batch_size_image_generation' in kwargs   :   batch_size_image_generation  = kwargs.pop('batch_size_image_generation')
        if gen_new_images is None:
            gen_new_images = False

        if data_dir:
            self.data_dir              =    data_dir
        if num_channels:
            self.num_channels          =    num_channels
        if lr:
            self.lr                    =    lr
        if batch_size:
            self.batch_size            =    batch_size
        if image_size:
            self.image_size            =    image_size

        if log_interval:
            self.log_interval          =    log_interval
        if save_interval:
            self.save_interval         =    save_interval
        if ema_rate:
            self.ema_rate              =    ema_rate
        if diffusion:
            self.diffusion             =    diffusion
        if network:
            self.network               =    network  
        if path_saved_model: 
            self.path_saved_model      =    path_saved_model
        if path_saved_model and (gen_new_images is False):
            if os.path.exists(path_saved_model):
                files = glob.glob(path_saved_model + "/*")
                for file in files:
                    if os.path.isfile(file):                                                                                             
                        os.remove(file)
            else:                                                                                                                        
                os.mkdir(path_saved_model) 
        if ngpu:
            self.ngpu = ngpu
            if ngpu > 0:
                if torch.cuda.is_available():
                    self.device = torch.device("cuda:0")
                else:
                    self.device = torch.device("cpu")       
        if  clip_denoised:
            self.clip_denoised   =  clip_denoised
        if  num_samples:
            self.num_samples     =  num_samples
        if  batch_size_image_generation:
            self.batch_size_image_generation  =  batch_size_image_generation
        if clipping_threshold:
            self.clipping_threshold = clipping_threshold 
        self.training_iteration_counter = 0


    class ImageDataset(torch.utils.data.Dataset):                          
        """
        Source: https://github.com/openai/improved-diffusion

        Access the image dataset.  Its __getitem__ makes available one image at a time as a tensor.
        The Dataloader to be defined later creates tensor for a batch of images.
        """
        def __init__(self, image_size, image_paths):
            super(GenerativeDiffusion.ImageDataset, self).__init__()
            self.image_size = image_size
            self.image_paths = image_paths
    
        def __len__(self):
            return len(self.image_paths)
    
        def __getitem__(self, idx):
            path = self.image_paths[idx]
            pil_image = Image.open(path)
            width,height = pil_image.size
            if any( (width != 64, height != 64) ):
                pil_image = pil_image.resize( (64,64), Image.ANTIALIAS )
            arr = np.array(pil_image.convert("RGB"))   
            arr = arr.astype(np.float32) / 127.5 - 1
            return np.transpose(arr, [2, 0, 1])


    def run_code_for_training(self):
        """
        Somewhat modified version of the code at:   https://github.com/openai/improved-diffusion
        """
        quartile_losses_dict  = {'mse_loss' : 0.0, 'mse_loss_q3': 0.0, 'mse_loss_q2': 0.0, 'mse_loss_q1': 0.0, 'mse_loss_q0': 0.0, 
                                 'grad_norm': 0.0, 'iteration' : 0, 'samples' : 0 }

        def clear_quartile_losses_dict():
            for key in quartile_losses_dict:
                if key in ['mse_loss', 'mse_loss_q3', 'mse_loss_q2', 'mse_loss_q1', 'mse_loss_q0', 'grad_norm']:
                    quartile_losses_dict[key] = 0.0

        diffusion =  self.diffusion
        diffusion.update_betas_for_diffusion()
        network   =  self.network
        ## Note that network.parameters() returns a Python generator object:
        network_params = list(network.parameters())     
        opt = AdamW(network_params, lr=self.lr, weight_decay=0.0)
        ema_rate = [self.ema_rate]
        ema_params = [ copy.deepcopy(network_params) for _ in range(len(ema_rate))  ]
        network = network.to(self.device)
        
        def calc_loss_dict(diffusion, ts, losses):    
            """
            The loss that is calculated for backpropagation is only with regard to the neural network's ability 
            to match in the p-chain the posterior of the transition probability as used in the q-chain.  That loss
            is not a direct indicator of how the p-chain would perform with regard generating new images from 
            noise.  The quartile losses as calculated here are meant to address that problem.   Recall that for 
            generating a new image, you have to go through all T transitions in the p-chain.
            """
            for key, values in losses.items():
                oldval = quartile_losses_dict[key]
                quartile_losses_dict[key] = oldval * self.training_iteration_counter / (self.training_iteration_counter + 1) +  \
                                                                          values.mean().item() / (self.training_iteration_counter + 1)
                # Log the quantiles (four quartiles, in particular).          
                for sub_t, sub_loss in zip(ts.cpu().numpy(), values.detach().cpu().numpy()):
                    quartile = int(4 * sub_t / diffusion.num_diffusion_timesteps)
                    oldval = quartile_losses_dict[f"{key}_q{quartile}"]
                    quartile_losses_dict[f"{key}_q{quartile}"] = oldval * self.training_iteration_counter / (self.training_iteration_counter + 1) + \
                                                                                      sub_loss / (self.training_iteration_counter + 1)
        def _log_grad_norm():
            sqsum = 0.0
            for p in network.parameters():
                if p.grad is None: continue
                sqsum += (p.grad ** 2).sum().item()
            oldval = quartile_losses_dict["grad_norm"]
            quartile_losses_dict["grad_norm"] = oldval * self.training_iteration_counter / (self.training_iteration_counter + 1) + \
                                                                                 np.sqrt(sqsum) / (self.training_iteration_counter + 1)

        def _network_params_to_state_dict(network_params):
            state_dict = network.state_dict()
            for i, (name, _value) in enumerate(network.named_parameters()):
                assert name in state_dict
                state_dict[name] = network_params[i]
            return state_dict
    
        def load_data():
            print("creating data loader...")
            if os.path.exists(self.data_dir):  
                all_files = glob.glob(self.data_dir + "/*")  
            dataset = self.ImageDataset( self.image_size, all_files)
            loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True, num_workers=1, drop_last=True )
            while True:
                yield from loader
        data = load_data()

        print("training...")
        while True:
            opt.zero_grad()
            batch = next(data)
            batch = batch.to(self.device)
            ## Uniformly sample the 1000 integer timestep integers in the range (0, num_diffusion_timesteps)
            indices_np = np.random.choice(self.diffusion.num_diffusion_timesteps, size=(self.batch_size))
            t = torch.from_numpy(indices_np).long().to(self.device)
            losses = diffusion.training_losses( network, batch, t )
            calc_loss_dict( diffusion, t, {k: v for k, v in losses.items()} )
            loss = (losses["mse_loss"]).mean()
            loss.backward()
            _log_grad_norm()
            opt.step()
            for rate, params in zip(ema_rate, ema_params):
                update_ema(params, network_params, rate=rate)
            quartile_losses_dict['iteration'] =  self.training_iteration_counter
            quartile_losses_dict['samples']  =  self.training_iteration_counter * self.batch_size
            if self.training_iteration_counter % self.log_interval == 0:                
                d = quartile_losses_dict
                mse_loss_dict = {}
                names_deleted = []
                print("\n\n---------------------------")
                for (name, val) in d.items():
                    if "mse_loss" in name: 
                        mse_loss_dict[name] = val
                print("TRAINING ITERATION " + " : " + str("%d" % d["iteration"]))
                print()
                print("training samples used " + " : " + str("%d" % d["samples"]))
                print("grad_norm" + " : " + str("%.6f" % d['grad_norm']))
                print()
                for (name, val) in sorted(mse_loss_dict.items()):        
                    print(name + " : " + str("%.8f" % val))
                print("---------------------------\n\n")
                clear_quartile_losses_dict()
    
            if self.training_iteration_counter % self.save_interval == 0:                      
                print("\n\nSaving checkpoint at training iteration: %d\n\n" % self.training_iteration_counter)
                state_dict = _network_params_to_state_dict(network_params)
                filename = f"/ema_{rate}_{(self.training_iteration_counter):06d}.pt"
                torch.save(state_dict, self.path_saved_model + filename )
            self.training_iteration_counter += 1
        # Save the last checkpoint if it wasn't already saved.
        if (self.training_iteration_counter - 1) % self.save_interval != 0:
            state_dict = _network_params_to_state_dict(network_params)
            filename = f"/ema_{rate}_{(self.training_iteration_counter):06d}.pt"
            torch.save(state_dict, self.path_saved_model + filename )


#########################################     End of GenerativeDiffusion class  ###########################################
###########################################################################################################################




###########################################################################################################################
#######################################     Start Definition of Gaussian Diffusion     ####################################

def _extract_into_tensor(arr, timesteps, broadcast_shape):
    """
    Source:  https://github.com/openai/improved-diffusion

    Reformat the values in a 1-D numpy array supplied by the parameter 'arr' for a batch
    of indices.

    The parameter 'arr' refers to the numpy array of alpha-beta values mentioned on Slide
    162 of my Week 11 slides.

    The "batch of indices" refers to the 1D tensor of randomly chosen timestamps supplied
    through the parameter 'timesteps'.  For example, if the batch size for model training is
    8, the value of the parameter 'timestamps' will look like

              tensor([315, 541,  70,  49, 726, 818, 149, 160], device='cuda:0')

    with each timestamp chosen randomly from the range (1,999) when T=1000.

    The parameter 'broadcast_shape' is the standard (B,C,H,W) for a data tensor flowing
    through a network.  The goal of this function is to first convert 'arr' into a tensor
    and then to reshape the tensor to look like the one with four axes, as in the shape
    (B,C,H,W).  At the same time, we want the values in 'arr' to be along the batch axis of
    the outgoing tensor.
    """
    res = torch.from_numpy(arr).to(device=timesteps.device)[timesteps].float()
    while len(res.shape) < len(broadcast_shape):
        res = res[..., None]     ## Each iteration adds one more axis with no data
    return res.expand(broadcast_shape)


class GaussianDiffusion:
    """
    Source:  https://github.com/openai/improved-diffusion

    This class is for subjecting a training image to Markov transitions that inject small
    amounts of isotropic Gaussian noise into the image until you end with pure zero-mean
    isotropic Gaussian noise. For a theoretical description of the process, see how the
    q-chain works in my Week 11 slides.
    
    As for the changes from the GitHub code, I have dropped its subclass that was named
    SpacedDiffusion. The purpose served by that subclass is now taken care of by the method
    named "update_betas_for_diffusion()" in the class presented here. Other changes include
    dropping the associated classes ModelMeanType and ModelVarType and the code related to
    those classes from the main class shown below.,
    """
    def __init__( self, num_diffusion_timesteps ):

        self.num_diffusion_timesteps = num_diffusion_timesteps

        beta_start = 0.0001
        beta_end =   0.02
        betas = np.linspace( beta_start, beta_end, self.num_diffusion_timesteps, dtype=np.float64 )

        # Use float64 for accuracy.
        betas = np.array(betas, dtype=np.float64)
        self.betas = betas
        assert len(betas.shape) == 1, "betas must be 1-D"
        assert (betas > 0).all() and (betas <= 1).all()

        alphas = 1.0 - betas
        self.alphas_cumprod = np.cumprod(alphas, axis=0)    
        self.alphas_cumprod_prev = np.append(1.0, self.alphas_cumprod[:-1])
        self.alphas_cumprod_next = np.append(self.alphas_cumprod[1:], 0.0)
        assert self.alphas_cumprod_prev.shape == (self.num_diffusion_timesteps,)

        # Forward Markov Chain: Calculates q(x_t | x_{t-1}) for diffusion:
        self.sqrt_alphas_cumprod = np.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = np.sqrt(1.0 - self.alphas_cumprod)
        self.log_one_minus_alphas_cumprod = np.log(1.0 - self.alphas_cumprod)
        self.sqrt_recip_alphas_cumprod = np.sqrt(1.0 / self.alphas_cumprod)
        self.sqrt_recipm1_alphas_cumprod = np.sqrt(1.0 / self.alphas_cumprod - 1)

        # calculations for posterior q(x_{t-1} | x_t, x_0)
        self.posterior_variance = ( betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod) )
        # log calculation clipped because the posterior variance is 0 at the
        # beginning of the diffusion chain.
        self.posterior_log_variance_clipped = np.log( np.append(self.posterior_variance[1], self.posterior_variance[1:]) )
        self.posterior_mean_coef1 = ( betas * np.sqrt(self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod) )
        self.posterior_mean_coef2 = ( (1.0 - self.alphas_cumprod_prev)  *  np.sqrt(alphas)  / (1.0 - self.alphas_cumprod) )


    def update_betas_for_diffusion(self):
        """
        Presumably, this updating of the betas makes the diffusion process more robust when you
        skip timesteps to take advantage of the property of the Gaussian diffusion process that
        allows you to combine multiple timesteps into a single invocation of diffusion.
        """
        use_timesteps =  range(self.num_diffusion_timesteps)
        last_alpha_cumprod = 1.0
        new_betas = []
        for i, alpha_cumprod in enumerate(self.alphas_cumprod):
            if i in use_timesteps:
                new_betas.append(1 - alpha_cumprod / last_alpha_cumprod)
                last_alpha_cumprod = alpha_cumprod
        self.betas  = np.array(new_betas)


    def q_sample(self, x_start, t, noise):
        """
        Source:  https://github.com/openai/improved-diffusion

        This is in the forward q-chain. Given the training image x_0, it calculates q( x_t |
        x_0 ) for a randomly chosen timestep t.  The parameter x_start is is the same thing
        as x_0 in the slides.

        This is an implementation of Eq. (68) on Slide 154.
        """
        assert noise.shape == x_start.shape
        return ( _extract_into_tensor( self.sqrt_alphas_cumprod, t, x_start.shape)   *   x_start    +  
                 _extract_into_tensor( self.sqrt_one_minus_alphas_cumprod, t, x_start.shape)   *   noise
        )


    def q_posterior_mean_and_variance(self, x_start, x_t, t):
        """
        Source:  https://github.com/openai/improved-diffusion

        Compute the mean and variance of the diffusion posterior:

            q(x_{t-1} | x_t, x_0)

        In the forward direction, the transitions in the q-chain are from timestep t-1 to
        the timestep t. After having made the forward transition, we now want to use the
        Bayes' Rule to go "backwards" from t to t-1 in order to figure out the mean and the
        variance of the posterior probability distribution at the previous timestep t-1
        given that we have the value x_t and ALSO the starting value x_0.  These posterior
        estimates can then serve as the targets for the denoising neural network that is
        learning how best to make the FORWARD transition from timestep t to the timestep t-1
        in the reverse p-chain.
        """
        assert x_start.shape == x_t.shape
        posterior_mean = (
            _extract_into_tensor(self.posterior_mean_coef1, t, x_t.shape) * x_start
            + _extract_into_tensor(self.posterior_mean_coef2, t, x_t.shape) * x_t
        )
        posterior_variance = _extract_into_tensor(self.posterior_variance, t, x_t.shape)
        posterior_log_variance_clipped = _extract_into_tensor(  self.posterior_log_variance_clipped, t, x_t.shape  )
        assert (
            posterior_mean.shape[0]
            == posterior_variance.shape[0]
            == posterior_log_variance_clipped.shape[0]
            == x_start.shape[0]
        )
        return posterior_mean, posterior_variance, posterior_log_variance_clipped


    def predict_xstart_in_pchain( self, model, x, t, clip_denoised=True ):
        """
        Source:  https://github.com/openai/improved-diffusion

        This function seeks to predict the training image x0 at each timestep in the reverse
        p-chain.  For that it needs the output of the neural network as well as the p-chain
        variances calculated in the __init__() of the GaussianDiffusion class.  The
        parameter 'model' stands for the neural-netork being used. To understand what exact
        timestep corresponds to t, note that this function is invoked after the forward
        q-chain has made the t-1 to t transition.  Note that t will be set to a tensor of 
        timesteps, one for each batch sample.  When the parameter 'clip_denoised' is set to
        True, the output of the neural network is clipped to be in the interval [-1, 1].
        """
        B, C = x.shape[:2]
        assert t.shape == (B,)
        model_output = model(x, t)
        ##  See Section 3.1 of Ho et el. paper for why the variance of the output
        ##  of the neural network is set to the quantity self.posterior_variance that
        ##  was calculated in the __init__() of GaussianDiffusion class:
        model_variance, model_log_variance = self.posterior_variance, self.posterior_log_variance_clipped
        model_variance = _extract_into_tensor(model_variance, t, x.shape)
        model_log_variance = _extract_into_tensor(model_log_variance, t, x.shape)
        if clip_denoised:
            pred_xstart = self._predict_xstart_from_model_output(x_t=x, t=t, model_output=model_output).clamp(-1,1) 
        else:
            pred_xstart = self._predict_xstart_from_model_output(x_t=x, t=t, model_output=model_output)
        model_mean, _, _ = self.q_posterior_mean_and_variance( x_start=pred_xstart, x_t=x, t=t   )
        assert (
            model_mean.shape == model_log_variance.shape == pred_xstart.shape == x.shape
        )
        return {
            "mean": model_mean,
            "variance": model_variance,
            "log_variance": model_log_variance,
            "pred_xstart": pred_xstart,
        }


    def training_losses(self, model, x_start, t):
        """
        Source:  https://github.com/openai/improved-diffusion

        Compute training losses for a single timestep.

        :param model: the model to evaluate loss on.
        :param x_start: the [N x C x ...] tensor of inputs.
        :param t: a batch of timestep indices.
        :param noise: if specified, the specific Gaussian noise to try to remove.
        :return: a dict with the key "loss" containing a tensor of shape [N].
                 Some mean or variance settings may also have other keys.
        """

        def mean_flat(tensor):                                       
            """
            Take the mean over all non-batch dimensions.
            """
            return tensor.mean(dim=list(range(1, len(tensor.shape))))
        noise = torch.randn_like(x_start) 
        x_t = self.q_sample(x_start, t, noise)
        terms = {}
        model_output = model(x_t, t)
        target = noise
        assert model_output.shape == target.shape == x_start.shape
        terms["mse_loss"] = mean_flat((target - model_output) ** 2)
        return terms


    def _predict_xstart_from_model_output(self, x_t, t, model_output):
        """
        Source:  https://github.com/openai/improved-diffusion
        """
        assert x_t.shape == model_output.shape
        return (
            _extract_into_tensor(self.sqrt_recip_alphas_cumprod, t, x_t.shape) * x_t
            - _extract_into_tensor(self.sqrt_recipm1_alphas_cumprod, t, x_t.shape) * model_output
        )


    def p_sampler_for_image_generation( self, model, shape, device, clip_denoised=True ):
        """
        Based on the code at:   Source:  https://github.com/openai/improved-diffusion

        After the model has been trained, you can use this function to generate a batch
        of images by deploying the reverse p-chain through all its transitions.
        """
        assert isinstance(shape, (tuple, list))
        img = torch.randn(*shape, device=device)
        indices = list(range(self.num_diffusion_timesteps))[::-1]
        for i in indices:
            t = torch.tensor([i] * shape[0], device=device)
            with torch.no_grad():
                out = self.p_sample( model, img, t, clip_denoised=clip_denoised )
                img = out["sample"]
        return img


    def p_sample( self, model, x, t, clip_denoised=True ):
        """
        Source:  https://github.com/openai/improved-diffusion

        Sample x_{t-1} from the model at the given timestep.  Recall that the timestep t-1 comes AFTER 
        the timestep t in the p-chain.

        :param model: the model to sample from.
        :param x: the current tensor at x_{t-1}.
        :param t: the value of t, starting at 0 for the first diffusion step.
        :param clip_denoised: if True, clip the x_start prediction to [-1, 1].
        :return: a dict containing the following keys:
                 - 'sample': a random sample from the model.
                 - 'pred_xstart': a prediction of x_0.
        """
        out = self.predict_xstart_in_pchain( model, x, t, clip_denoised=clip_denoised )
        noise = torch.randn_like(x)
        nonzero_mask = (  (t != 0).float().view(-1, *([1] * (len(x.shape) - 1)))  )  # no noise when t == 0
        sample = out["mean"] + nonzero_mask * torch.exp(0.5 * out["log_variance"]) * noise
        return {"sample": sample}


#############################################   END of Gaussian Diffusion  ################################################
###########################################################################################################################    


###########################################################################################################################
############################################### Start of Class UNetModel ##################################################


class AttentionBlock(torch.nn.Module):        
    """
    Source:  https://github.com/openai/improved-diffusion

    I am assuming that you already have a good understanding of QKV Attention as originally
    formulated in the Vaswani et al paper on Transformers and how the same attention
    mechanism was used in the Vision Transformer, ViT.  There are significant differences in
    those formulations of Attention and how the same concept works here for the case of
    diffusion.

    If you are not familiar with the original formulation of Attention as mentioned above,
    you might wish to consult my Week 14 Slides at the Deep Learning website at Purdue.

    The notion of the embedding vector representation of the basic units of the input data
    plays a fundamental role in the original formulation of Attention.  For example, in
    seq-2-seq learning for language translation, each word in a sentence will be represented
    by an embedding vector of size M of floating-point numbers. Single-headed attention
    consists of associating with each embedding vector a Query vector Q, a Key vector K, and
    a Value vector V.  The QKV vectors for the different input units interact through
    dot-products for each input unit to figure out how it should attend to the other input
    units.  And that's what's referred to as the Attention mechanism.  Multi-headed
    attention does the same thing but by first segmenting the embedding vectors into P
    segments where P is the number of Attention Heads.  Subsequently, the QKV attention is
    calculated for each segment in exactly the same manner as for Single-headed attention.

    The same notion is used in UNetModel for inter-pixel attention at a couple of different
    levels in the UNet. The data that is input into the UNet is of shape (B,C,H,W). For
    calculating the inter-pixel attention, for each pixel in the HxW array, we consider the
    C floating-point values along the channel axis as the embedding vector representation of
    that pixel.  And, then, speaking a bit loosely, the rest is the same as before.  More
    accurately, though, we do two things before invoking Attention in this manner: (1) We
    first flatten the HxW array of pixels into a 1-dimensional pixel array --- just to make
    it easier to write the dot-product code later. (2) We use a 1-dimensional convolution on
    the 1-dimensional array of pixels to convert the C channels associated with each pixel
    into a 3*C channels. Since the channel axis is used as the embedding vector at each
    pixel, increasing the number of channels gives us more latitude in dividing the channel
    axis into portions reserved for Q, K, and V.  For a deeper reason as to why we need this
    C-channel to 3*C-channel transformation of the input, read the end of the next
    paragraph.
    
    An interesting difference between the formulation of Attention as in Vaswani et al. and
    the same mechanism for inter-pixel attention as implemented below is the absence of the
    matrices that multiply the embedding vectors for the calculation of Q, K, and V.  In
    what follows, those three matrices are incorporated implicitly in the matrix operator
    used for the 1-dimensional convolution carried out by 'self.qkv' that is declared in the
    constructor shown below. It is this operator that increases the the number of output
    channels from C to 3*C. Since, under the hood, a convolution in PyTorch is implemented
    with a matrix-vector product (as explained in my Week 8 slides at the Purdue DL
    website), we can conceive of the matrix being segmented along its row-axis into three
    different parts, one that outputs the Q vector, the second that outputs the K vector,
    and third that output the V vector.
    """
    def __init__(self, time_embed_dim, num_heads=1, use_checkpoint=False):
        super().__init__()
        self.time_embed_dim = time_embed_dim
        self.num_heads = num_heads
        self.norm = nn.GroupNorm(32, time_embed_dim)
        self.qkv = nn.Conv1d(time_embed_dim, time_embed_dim * 3, 1)
        self.proj_out = zero_module(nn.Conv1d(time_embed_dim, time_embed_dim, 1))

    def forward(self, x):
        ##  The variable 'x' starts out being of shape (B,C,H,W). The following statement stores
        ##  away the (H,W) spatial dimensions of the input. That is, the variable 'spatial' will be
        ##  set to (H,W) of the image input x:
        b, im_channels, *spatial = x.shape

        ##  The number of channels in the input image needs to be the same as the 'time_embed_dim'
        assert(x.shape[1] == self.time_embed_dim)

        ##  From this point on, the shape of the input will change from (B,C,H,W) to (B,C,H*W).  
        ##  That is, up to this point, the pixels formed a 2D array of shape HxW.  But, from this point, 
        ##  they will constitute a 1D signal with H*W pixels in it.  So, if H=W=16, we will basically 
        ##  end up with a 1-dimensional signal or a single vector with 256 elements.
        x = x.reshape(b, self.time_embed_dim, -1)

        ##  The 1-dimensional convolution called for by self.qkv below changes the shape of the input
        ##  from (B,C,H*W) to (B,3*C,H*W).  So we are tripling the number of channels in the
        ##  1-dimensional representation of the input data.  For single-headed attention, the idea
        ##  is to use the first set of the C output channels for Q, the second set of C channels for
        ##  K, and the third set of C channels for V --- a la Vaswani transformers.  For
        ##  multi-headed attention, we would first divide the 3*C channels amongst the different
        ##  heads, and then, for each head, divide the channels by 3 for specifying the channels for
        ##  Q, K, and V.
        ##
        ##  Next Consider Multi-Headed Attention:
        ##
        ##  Let's assume that you are planning to use N heads. You will still divide the 3*C
        ##  channels into three equal parts as for the case of single-headed attention.  However,
        ##  you will divide the 3*C channels amongst the N heads.  That is, each head will get
        ##  (3*C)/N channels.  And, for each, you would divide the (3*C)/N channels amongst Q, K,
        ##  and V.  It would amount to assigning C/N channels to each of Q, K, and V, for every
        ##  attention head.
        qkv = self.qkv(self.norm(x))                                   

        ##  Note that the variable qkv defined above is just the same as the input x with its
        ##  pixels in the flattened vector and with its number of channels three times the number
        ##  of input channels.

        ##  In the following statement, note that qkv.shape[2] equals the total number of pixels in
        ##  the input --- although now they are in the form of a flattened vector.  The tensor
        ##  reshaping shown below allows each attention head to operate independently on its section
        ##  of the channel Axis.  It is independent in the same sense as would be case for
        ##  processing of each batch instance. Therefore, for applying the QKV attention formula, we
        ##  can place each attention head on the same footing as each batch instance.
        qkv = qkv.reshape(b * self.num_heads, -1, qkv.shape[2])              

        ##  Now we are ready to invoke Vaswani's formula for QKV attention.  The following returns 
        ##  the number of channels to be devoted to each of Q, K, V in each attention head.
        ch = qkv.shape[1] // 3

        ##  This splits the channel axis of the qkv tensor into three parts along the channel axis.
        q, k, v = torch.split(qkv, ch, dim=1)

        ##  This calculates the denominator needed for Eq. (3) on Slide 18 of my Week 18 Lecture on
        ##  transformers:
        scale = 1 / math.sqrt(math.sqrt(ch))

        ##  Caculating the attention means computing (Q.K^T)V.  The statement below calculates the dot                           
        ##  product Q.K^T.  See Eq. (3) on Slide 18:
        weight = torch.einsum( "bct,bcs->bts", q * scale, k * scale )  

        ##  Subsequently, you torch.softmax() to the product (Q.K^T):        
        weight = torch.softmax(weight.float(), dim=-1).type(weight.dtype)

        ##  And, finally, multiply the above result with V:
        h  =  torch.einsum("bts,bcs->bct", weight, v)

        h = h.reshape(b, -1, h.shape[-1])
        h = self.proj_out(h)
        return (x + h).reshape(b, im_channels, *spatial)


class UNetModel(nn.Module):
    """
    Source:  https://github.com/openai/improved-diffusion

    :param in_channels: channels in the input Tensor.
    :param model_channels: base channel count for the model.
    :param out_channels: channels in the output Tensor.
    :param num_res_blocks: number of residual blocks per downsample.
    :param attention_resolutions: a collection of downsample rates at which
        attention will take place. May be a set, list, or tuple.
        For example, if this contains 4, then at 4x downsampling, attention
        will be used.
    :param channel_mult: channel multiplier for each level of the UNet.
    :param num_heads: the number of attention heads in each attention layer.
    """

    def __init__(
        self,
        in_channels,
        model_channels,
        out_channels,
        num_res_blocks,
        attention_resolutions,
        channel_mult=(1, 2, 4, 8),
        num_heads=1,
        attention = True
    ):
        super().__init__()
        self.in_channels = in_channels
        self.model_channels = model_channels
        self.out_channels = out_channels
        self.num_res_blocks = num_res_blocks
        self.attention_resolutions = attention_resolutions                                        
        self.channel_mult = channel_mult
        self.num_heads = num_heads
        self.attention = attention
        time_embed_dim = model_channels * 4


        ##------------------------------  Inner utility classes for UNetModel ------------------------
        class SiLU(torch.nn.Module):
            def forward(self, x):
                return x * torch.sigmoid(x)

        class TimestepBlock(nn.Sequential, nn.Module):   
            """
            A sequential module that passes timestep embeddings to the children that
            support it as an extra input.
            """
            def forward(self, x, emb):
                for layer in self:
                    if isinstance(layer, TimestepBlock):
                        x = layer(x, emb)
                    else:
                        x = layer(x)
                return x

        class Upsample(nn.Module):                              
            def __init__(self, channels ):
                super().__init__()
                self.channels = channels
                self.conv = nn.Conv2d(channels, channels, 3, padding=1)
        
            def forward(self, x):
                assert x.shape[1] == self.channels
                x = F.interpolate(x, scale_factor=2, mode="nearest")
                x = self.conv(x)
                return x
        
        class Downsample(nn.Module):                                      
            def __init__(self, channels):
                super().__init__()
                self.channels = channels
                stride = 2
                self.op = nn.Conv2d(channels, channels, 3, stride=stride, padding=1)
        
            def forward(self, x):
                assert x.shape[1] == self.channels
                return self.op(x)
        
        class ResBlock(TimestepBlock):                                                            
            """
            A residual block that can OPTIONALLY change the number of channels.
            :param channels: the number of input channels.
            :param emb_channels: the number of timestep embedding channels.
            :param out_channels: if specified, the number of out channels.
            :param use_conv: if True and out_channels is specified, use a spatial
                convolution instead of a smaller 1x1 convolution to change the
                channels in the skip connection.
            """
            def __init__(self, channels, emb_channels, out_channels=None):
                super().__init__()
                self.channels = channels
                self.emb_channels = emb_channels              ## number of timestep embedding channels
                self.out_channels = out_channels or channels
        
                class SiLU(nn.Module):
                    def forward(self, x):
                        return x * torch.sigmoid(x)
        
                self.in_layers = nn.Sequential(
                    nn.GroupNorm(32, channels),
                    SiLU(),
                    nn.Conv2d(channels, self.out_channels, 3, padding=1),
                )
                self.emb_layers = nn.Sequential(
                    SiLU(),
                    nn.Linear(emb_channels, self.out_channels),
                )
                self.out_layers = nn.Sequential(
                    nn.GroupNorm(32, self.out_channels),
                    SiLU(),
                    zero_module(
                        nn.Conv2d(self.out_channels, self.out_channels, 3, padding=1)
                    ),
                )
        
                if self.out_channels == channels:
                    self.skip_connection = nn.Identity()
                self.skip_connection = nn.Conv2d(channels, self.out_channels, 1)
        
            def forward(self, x, emb):
                h = self.in_layers(x)
                emb_out = self.emb_layers(emb).type(h.dtype)
                while len(emb_out.shape) < len(h.shape):
                    emb_out = emb_out[..., None]
                h = h + emb_out
                h = self.out_layers(h)
                return self.skip_connection(x) + h
        ##----------------------  END END of Inner utility classes for UNetModel ---------------------
        

        self.time_embed = nn.Sequential(
            nn.Linear(model_channels, time_embed_dim),
            SiLU(),
            nn.Linear(time_embed_dim, time_embed_dim),
        )

        self.input_blocks = nn.ModuleList( [ TimestepBlock( nn.Conv2d( in_channels, model_channels, 3, padding=1 ) ) ] )
        input_block_chans = [model_channels]
        ch = model_channels
        ds = 1
        for level, mult in enumerate(channel_mult):
            for _ in range(num_res_blocks):
                layers = [ ResBlock( ch, time_embed_dim, out_channels=mult * model_channels ) ]
                ch = mult * model_channels
                if self.attention:
                    if ds in attention_resolutions:
                        layers.append( AttentionBlock( ch, num_heads=num_heads ) )
                self.input_blocks.append(TimestepBlock(*layers))
                input_block_chans.append(ch)
            if level != len(channel_mult) - 1:
                self.input_blocks.append( TimestepBlock(Downsample(ch)) )
                input_block_chans.append(ch)
                ds *= 2

        if self.attention:
           self.middle_block = TimestepBlock( ResBlock( ch, time_embed_dim ), AttentionBlock(ch, num_heads=num_heads), ResBlock( ch, time_embed_dim ) )
        else:
           self.middle_block = TimestepBlock( ResBlock( ch, time_embed_dim ), ResBlock( ch, time_embed_dim ) )

        self.output_blocks = torch.nn.ModuleList([])
        for level, mult in list(enumerate(channel_mult))[::-1]:
            for i in range(num_res_blocks + 1):
                layers = [ ResBlock( ch + input_block_chans.pop(), time_embed_dim, out_channels=model_channels * mult ) ]
                ch = model_channels * mult
                if self.attention:
                    if ds in attention_resolutions:
                        layers.append( AttentionBlock( ch ) )
                if level and i == num_res_blocks:
                    layers.append( Upsample(ch) )
                    ds //= 2
                self.output_blocks.append(TimestepBlock(*layers))

        self.out = nn.Sequential(
            nn.GroupNorm(32, ch),
            SiLU(),
            zero_module(nn.Conv2d(model_channels, out_channels, 3, padding=1)),
        )

    def forward(self, x, timesteps, y=None):
        hs = []
        emb = self.time_embed(timestep_embedding(timesteps, self.model_channels))
        h = x.type(self.inner_dtype)
        for module in self.input_blocks:
            h = module(h, emb)
            hs.append(h)

        h = self.middle_block(h, emb)
        for module in self.output_blocks:
            cat_in = torch.cat([h, hs.pop()], dim=1)
            h = module(cat_in, emb)
        h = h.type(x.dtype)
        return self.out(h)

    @property
    def inner_dtype(self):
        """
        Required by the forward() of this class, UNetModel
        Get the dtype used by the torso of the model.
        """
        return next(self.input_blocks.parameters()).dtype

#################################################   End of UNetModel Class ################################################
###########################################################################################################################


###########################################################################################################################
################################################# Start of Class mUNet ####################################################

class mUNet(nn.Module):
    """
    I have included this class here as a "remote possibility" replacement for the UNetModel class in the code
    shown above.  To test out that role for this class will require considerable hyperparameter tuning of at least
    the beta coefficients.  I have not yet had time to do that.  
    """

    def __init__(self, in_channels, model_channels, out_channels, skip_connections=True, depth=16):
        super().__init__()

        self.in_channels = in_channels
        self.model_channels = model_channels
        self.out_channels = out_channels

        self.time_embed_dim = self.model_channels * 4 * 24

        self.depth = depth // 2
        self.conv_in = nn.Conv2d(3, 64, 3, padding=1)

        time_embed_dim = self.time_embed_dim



        ##------------------------------  Inner utility classes for mUNet ----------------------------
        class SiLU(torch.nn.Module):
            def forward(self, x):
                return x * torch.sigmoid(x)

        class SkipBlockDN(nn.Module):
            def __init__(self, in_ch, out_ch, downsample=False, skip_connections=True):
                super(SkipBlockDN, self).__init__()
                self.downsample = downsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convo1 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.convo2 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.bn1 = nn.BatchNorm2d(out_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                if downsample:
                    self.downsampler = nn.Conv2d(in_ch, out_ch, 1, stride=2)
            def forward(self, x):
                identity = x                                     
                out = self.convo1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                if self.in_ch == self.out_ch:
                    out = self.convo2(out)                              
                    out = self.bn2(out)                              
                    out = nn.functional.relu(out)
                if self.downsample:
                    out = self.downsampler(out)
                    identity = self.downsampler(identity)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity
                    else:
                        out = out + torch.cat((identity, identity), dim=1) 
                return out
        
        class SkipBlockUP(nn.Module):
            def __init__(self, in_ch, out_ch, upsample=False, skip_connections=True):
                super(SkipBlockUP, self).__init__()
                self.upsample = upsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convoT1 = nn.ConvTranspose2d(in_ch, out_ch, 3, padding=1)
                self.convoT2 = nn.ConvTranspose2d(in_ch, out_ch, 3, padding=1)
                self.bn1 = nn.BatchNorm2d(out_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                if upsample:
                    self.upsampler = nn.ConvTranspose2d(in_ch, out_ch, 1, stride=2, dilation=2, output_padding=1, padding=0)
            def forward(self, x):
                identity = x                                     
                out = self.convoT1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                out  =  nn.ReLU(inplace=False)(out)            
                if self.in_ch == self.out_ch:
                    out = self.convoT2(out)                              
                    out = self.bn2(out)                              
                    out = nn.functional.relu(out)
                if self.upsample:
                    out = self.upsampler(out)
                    identity = self.upsampler(identity)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity                              
                    else:
                        out = out + identity[:,self.out_ch:,:,:]
                return out
        ##----------------------  END END of Inner utility classes for mUNet  ------------------------        

        self.time_embed = torch.nn.Sequential(
            torch.nn.Linear(self.model_channels, time_embed_dim),
            SiLU(),
            torch.nn.Linear(time_embed_dim, time_embed_dim),
        )
        ##  For the DN arm of the U:
        self.bn1DN  = nn.BatchNorm2d(64)
        self.bn2DN  = nn.BatchNorm2d(128)
        self.skip64DN_arr = nn.ModuleList()
        for i in range(self.depth):
            self.skip64DN_arr.append(SkipBlockDN(64, 64, skip_connections=skip_connections))
        self.skip64dsDN = SkipBlockDN(64, 64,   downsample=True, skip_connections=skip_connections)
        self.skip64to128DN = SkipBlockDN(64, 128, skip_connections=skip_connections )
        self.skip128DN_arr = nn.ModuleList()
        for i in range(self.depth):
            self.skip128DN_arr.append(SkipBlockDN(128, 128, skip_connections=skip_connections))
        self.skip128dsDN = SkipBlockDN(128,128, downsample=True, skip_connections=skip_connections)
        ##  For the UP arm of the U:
        self.bn1UP  = nn.BatchNorm2d(128)
        self.bn2UP  = nn.BatchNorm2d(64)
        self.skip64UP_arr = nn.ModuleList()
        for i in range(self.depth):
            self.skip64UP_arr.append(SkipBlockUP(64, 64, skip_connections=skip_connections))
        self.skip64usUP = SkipBlockUP(64, 64, upsample=True, skip_connections=skip_connections)
        self.skip128to64UP = SkipBlockUP(128, 64, skip_connections=skip_connections )
        self.skip128UP_arr = nn.ModuleList()
        for i in range(self.depth):
            self.skip128UP_arr.append(SkipBlockUP(128, 128, skip_connections=skip_connections))
        self.skip128usUP = SkipBlockUP(128,128, upsample=True, skip_connections=skip_connections)
        self.conv_out = nn.ConvTranspose2d(64, 3, 3, stride=2,dilation=2,output_padding=1,padding=2)

    def forward(self, x, timesteps):
        emb = self.time_embed(timestep_embedding(timesteps, self.model_channels))
        x += emb.view(x.shape)         
        ##  Going down to the bottom of the U:
        x = nn.MaxPool2d(2,2)(nn.functional.relu(self.conv_in(x)))          
        for i,skip64 in enumerate(self.skip64DN_arr[:self.depth//4]):
            x = skip64(x)                
        num_channels_to_save1 = x.shape[1] // 2
        save_for_upside_1 = x[:,:num_channels_to_save1,:,:].clone()
        x = self.skip64dsDN(x)
        for i,skip64 in enumerate(self.skip64DN_arr[self.depth//4:]):
            x = skip64(x)                
        x = self.bn1DN(x)
        num_channels_to_save2 = x.shape[1] // 2
        save_for_upside_2 = x[:,:num_channels_to_save2,:,:].clone()
        x = self.skip64to128DN(x)
        for i,skip128 in enumerate(self.skip128DN_arr[:self.depth//4]):
            x = skip128(x)                

        x = self.bn2DN(x)
        num_channels_to_save3 = x.shape[1] // 2
        save_for_upside_3 = x[:,:num_channels_to_save3,:,:].clone()
        for i,skip128 in enumerate(self.skip128DN_arr[self.depth//4:]):
            x = skip128(x)                
        x = self.skip128dsDN(x)
        ## Coming up from the bottom of U on the other side:
        x = self.skip128usUP(x)          
        for i,skip128 in enumerate(self.skip128UP_arr[:self.depth//4]):
            x = skip128(x)                
        x[:,:num_channels_to_save3,:,:] =  save_for_upside_3
        x = self.bn1UP(x)
        for i,skip128 in enumerate(self.skip128UP_arr[:self.depth//4]):
            x = skip128(x)                
        x = self.skip128to64UP(x)
        for i,skip64 in enumerate(self.skip64UP_arr[self.depth//4:]):
            x = skip64(x)                
        x[:,:num_channels_to_save2,:,:] =  save_for_upside_2
        x = self.bn2UP(x)
        x = self.skip64usUP(x)
        for i,skip64 in enumerate(self.skip64UP_arr[:self.depth//4]):
            x = skip64(x)                
        x[:,:num_channels_to_save1,:,:] =  save_for_upside_1
        x = self.conv_out(x)
        return x
##################################################   End of mUNet Class  ##################################################
###########################################################################################################################



###########################################################################################################################
############################################## Start of utilty functions ##################################################

def timestep_embedding(timesteps, dim, max_period=10000):  
    """
    Source:  https://github.com/openai/improved-diffusion

    Create sinusoidal timestep embeddings.

    :param timesteps: a 1-D Tensor of N indices, one per batch element.
                      These may be fractional.
    :param dim: the dimension of the output.
    :param max_period: controls the minimum frequency of the embeddings.
    :return: an [N x dim] Tensor of positional embeddings.
    """
    half = dim // 2
    freqs = torch.exp(
        -math.log(max_period) * torch.arange(start=0, end=half, dtype=torch.float32) / half
    ).to(device=timesteps.device)
    args = timesteps[:, None].float() * freqs[None]
    embedding = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
    if dim % 2:
        embedding = torch.cat([embedding, torch.zeros_like(embedding[:, :1])], dim=-1)
    return embedding

def update_ema(target_params, source_params, rate=0.99):                   
    """
    Source:  https://github.com/openai/improved-diffusion

    Update target parameters to be closer to those of source parameters using
    an exponential moving average.

    :param target_params: the target parameter sequence.
    :param source_params: the source parameter sequence.
    :param rate: the EMA rate (closer to 1 means slower).
    """
    for targ, src in zip(target_params, source_params):                    
        targ.detach().mul_(rate).add_(src.cpu(), alpha=1 - rate)

def zero_module(module):                                                
    """
    Source:  https://github.com/openai/improved-diffusion
    Zero out the parameters of a module and return it.
    """
    for p in module.parameters():
        p.detach().zero_()
    return module

############################################### End of utilty functions ###################################################
###########################################################################################################################



##______________________________    Test code follows    _________________________________

if __name__ == '__main__': 
    pass
