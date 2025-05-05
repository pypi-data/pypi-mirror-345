
##  GenerateNewImageSamples.py

##  After you have trained the model, use this script to generate new images that should like those
##  in your training dataset.

##  The call syntax should look like
##
##            python3 GenerateNewImageSamples.py  --model_path  RESULTS/ema_0.9999_020000.pt
##
##  if you are generating images from the checkpoint that was created at the training iteration
##  indexed 20,000.

##  See the README in the ExamplesDiffusion directory for how to use this script for
##  generating the images from a model checkpoint created by the script RunCodeForDiffusion.py

##  watch -d -n 0.5 nvidia-smi


import os
import sys
import numpy as np

import torch

if len(sys.argv) < 3:
    sys.exit("\n\nExample Call Syntax:  python3 GenerateNewImageSamples.py  --model_path  RESULTS/ema_0.9999_020000.pt\n\n")

from GenerativeDiffusion import *

gauss_diffusion   =  GaussianDiffusion(
                        num_diffusion_timesteps = 1000,

                    )


network =  UNetModel(
                       in_channels=3,
                       model_channels   =  128,
                       out_channels     =  3,
                       num_res_blocks   =  2,
                       attention_resolutions =  (4, 8),               ## for 64x64 images
                       channel_mult     =    (1, 2, 3, 4),            ## for 64x64 images
                       num_heads        =    1,
                       attention        =    True            ## <<< Must be the same as for RunCodeForDiffusion.py
#                       attention        =    False          ## <<< Must be the same as for RunCodeForDiffusion.py

                     )


top_level = GenerativeDiffusion(
                        gen_new_images        =        True,
                        image_size            =        64,
                        num_channels          =        128,
                        ema_rate              =        0.9999,
                        diffusion = gauss_diffusion,
                        network = network,
                        ngpu = 1,
                        path_saved_model = "RESULTS",
                        clip_denoised=True,
                        num_samples=32, 
                        batch_size_image_generation=8,
             )   

if sys.argv[1] == '--model_path':
    model_path = sys.argv[2]


network.load_state_dict( torch.load(model_path) )

network.to(top_level.device)
network.eval()

print("sampling...")
all_images = []

while len(all_images) * top_level.batch_size_image_generation < top_level.num_samples:
    sample = gauss_diffusion.p_sampler_for_image_generation(
        network,
        (top_level.batch_size_image_generation, 3, top_level.image_size, top_level.image_size),
        device = top_level.device,
        clip_denoised = top_level.clip_denoised,
    )
    sample = ((sample + 1) * 127.5).clamp(0, 255).to(torch.uint8)
    sample = sample.permute(0, 2, 3, 1)
    sample = sample.contiguous()
    gathered_samples = [sample]
    all_images.extend([sample.cpu().numpy() for sample in gathered_samples])
    print(f"created {len(all_images) * top_level.batch_size_image_generation} samples")

arr = np.concatenate(all_images, axis=0)
arr = arr[: top_level.num_samples]

shape_str = "x".join([str(x) for x in arr.shape])
out_path = os.path.join(top_level.path_saved_model, f"samples_{shape_str}.npz")

np.savez(out_path, arr)

print("image generation completed")

