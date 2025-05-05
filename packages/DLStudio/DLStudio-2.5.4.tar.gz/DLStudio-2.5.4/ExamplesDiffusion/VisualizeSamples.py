
##  VisualizeSamples.py

##  Avi Kak, March 2024

##  See the README in the ExamplesDiffusion directory for how to use this script for
##  extracting the images from the numpy archive created by the script
##  GenerateNewImageSamples.py


import os,sys
import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
import glob
from PIL import Image

print("\n\nPutting together a collage of the generated images for display\n")
print("\nFor the individual images, check the directory 'visualize_samples'\n\n")


npz_archive = "RESULTS/samples_32x64x64x3.npz"        ##  You must change this as needed.  The first number, 32,
                                                      ##  is the batch-size used for sampling a checkpoint.  It
                                                      ##  is set in the script GenerateNewImageSamples.py.
                                                      ##
                                                      ##  In our case, an npz archive is a dict with a single 
                                                      ##  'key-value' pair.  The name of the 'key' is 'arr_0'.  
                                                      ##  And the shape of the 'value' will be the shape of the 
                                                      ##  ndarray that stores the generated images. For the example 
                                                      ##  shown, the shape of the value is (32,64,64,3)
visualization_dir  =  "visualize_samples"
image_display_size = (256,256)


if os.path.exists(visualization_dir):
    files = glob.glob(visualization_dir + "/*")
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
else:
    os.mkdir(visualization_dir)

data = np.load(npz_archive)

for i, arr in enumerate(data['arr_0']):
    img = Image.fromarray( arr )
    img = img.resize( image_display_size )
    img.save( f"visualize_samples/test_{i}.jpg" )


if os.path.exists(visualization_dir):
    im_tensor_all = torch.from_numpy(data['arr_0']).float()
    im_tensor_all = torch.transpose(im_tensor_all, 1,3)
    im_tensor_all = torch.transpose(im_tensor_all, 2,3)
    plt.figure(figsize=(25,15))   
    plt.imshow( np.transpose( torchvision.utils.make_grid(im_tensor_all, padding=2, pad_value=1, normalize=True).cpu(), (1,2,0) )  )
    plt.title("Fake Images")
    plt.savefig(visualization_dir +  "/fake_images.png")
    plt.show()

