##  RunCodeForDiffusion.py

"""
IMPORTANT NOTE:  

    You will need to install the PurdueShapes5GAN dataset before you can execute this script.

    Download the dataset archive

            datasets_for_AdversarialLearning.tar.gz

    through the link "Download the image dataset for AdversarialLearning and Diffusion" provided 
    at the top of main doc page for DLStudio and store it in the

            ExamplesDiffusion

    directory of the distribution.  Subsequently, execute the following command in that directory:

            tar zxvf datasets_for_AdversarialLearning.tar.gz

    This command will create a 'dataGAN' subdirectory and deposit the following dataset archive
    in that subdirectory:

            PurdueShapes5GAN-20000.tar.gz

    Now execute the following in the "dataGAN" directory:

            tar zxvf PurdueShapes5GAN-20000.tar.gz

    With that, you should be able to execute the diffusion related scripts in the 'ExamplesDiffusion' 
    directory.
"""

##  About this script:

##  This is the script you must execute for training a diffusion based model for your 
##  training data.

##  See the README in the ExamplesDiffusion directory for how to use this script for
##  training a diffusion model.

##  watch -d -n 0.5 nvidia-smi



from GenerativeDiffusion import *

gauss_diffusion   =  GaussianDiffusion( num_diffusion_timesteps = 1000 )

network =  UNetModel(
                       in_channels=3,
                       model_channels   =  128,
                       out_channels     =  3,
                       num_res_blocks   =  2,
                       attention_resolutions =  (4, 8),       
                       channel_mult     =    (1, 2, 3, 4),    
                       num_heads        =    1,
                       attention        =    True             ## <<<< Make sure that GenerateNewImageSamples.py has the same
#                       attention        =    False           ## <<<< Make sure that GenerateNewImageSamples.py has the same
                     )


top_level = GenerativeDiffusion (
                        data_dir = "./dataGAN/PurdueShapes5GAN/multiobj/0/",
#                        data_dir="/home/kak/ImageDatasets/PurdueShapes5GAN/multiobj/0/",
#                        data_dir = "/mnt/cloudNAS3/Avi/ImageDatasets/PurdueShapes5GAN/multiobj/0/",

                        image_size            =        64,
                        num_channels          =        128,

                        lr=1e-4,

#                        batch_size=8,                     ## for laptop based debugging
                        batch_size=32,                     ## on RVL Cloud

#                        log_interval=10,                  ## for laptop based debugging
#                        save_interval=100,                ## for laptop based debugging
                        log_interval=100,
                        save_interval=10000,

                        ema_rate  = 0.9999,
                        diffusion = gauss_diffusion,
                        network = network,
                        ngpu = 1,
                        path_saved_model = "RESULTS"
             )   


top_level.run_code_for_training()

