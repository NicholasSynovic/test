import cv2
import torch
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
# import os

def get_argparse():
    parser = ArgumentParser(
        prog="quick start with midas model",
        usage="This generates inverse depth map of an image using Midas model",
    )
    parser.add_argument(
        "-i",
        "--image",
        help="image for the model",
        type=str,
        # required=True,
        required=False,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="optional, select model to use: 0: DPT_Large, 1: DPT_Hybrid, 2: MiDaS_small, default -> 2: small",
        default=2,
        type=int,
        required=False,
    )
    parser.add_argument(
        "-f",
        "--folder",
        help="Pass a folder of images",
        type=str,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--threshold",
        help="optional, threshold value for mask generating",
        default=0.7,
        type=float,
        required=False,
    )
    return parser

def get_midas(model_type):
    midas = torch.hub.load("intel-isl/MiDaS", model_type)
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu") # pylint: disable=no-member
    midas.to(device)

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
        transform = midas_transforms.dpt_transform
    else:
        transform = midas_transforms.small_transform

    return midas, transform, device

def depth(img, midas, transform, device):
    img_tr = cv2.imread(img) # pylint: disable=no-member
    img_tr = cv2.cvtColor(img_tr, cv2.COLOR_BGR2RGB) # pylint: disable=no-member

    input_batch = transform(img_tr).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_tr.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    output = prediction.cpu().numpy()
    return output


def get_folder_images(folder_name):
    """
    Gets images from folder 
    """
    image_exts = (".jpg", ".jpeg", ".png")
    images_path = [os.path.join(folder_name,_) for _ in os.listdir(folder_name) if _.lower().endswith(image_exts)]
    images_ = [_ for _ in os.listdir(folder_name) if _.lower().endswith(image_exts)]
    return images_path, images_

# def output_depth_map_image_file(file_name,model):
#     models = ["DPT_Large","DPT_Hybrid", "MiDaS_small"]
#     output = "dept_map_" + models[model]+ "_" + file_name 
#     midas, transform, device = get_midas(models[model])
#     depth_ = depth(file_name, midas, transform, device)
#     plt.imshow(depth_)
#     plt.savefig(output)

# def output_depth_map_image_folder(folder_name,model):
#     models = ["DPT_Large","DPT_Hybrid", "MiDaS_small"]
#     images_path, images_ = get_folder_images(folder_name)
#     output_path =  "depth_maps_" + folder_name
#     if not os.path.exists(output_path): os.makedirs(output_path)
#
#     for image_path,image_ in zip(images_path,images_):
#         output = "dept_map_" + models[model]+ "_" + image_ 
#         output = os.path.join(output_path,output)
#         midas, transform, device = get_midas(models[model])
#         depth_ = depth(image_path, midas, transform, device)
#         plt.imshow(depth_)
#         plt.savefig(output)

# take folder of images and output the depth map of images into a folder of csv files
def output_depth_map_array_folder(folder_name,model):
    models = ["DPT_Large","DPT_Hybrid", "MiDaS_small"]
    images_path, images_ = get_folder_images(folder_name)
    output_path =  "depth_maps_" + folder_name
    if not os.path.exists(output_path): os.makedirs(output_path)

    for image_path,image_ in zip(images_path,images_):
        output = "dept_map_" + models[model]+ "_" + image_ + ".csv"
        output = os.path.join(output_path,output)
        midas, transform, device = get_midas(models[model])
        depth_ = depth(image_path, midas, transform, device)
        # plt.imshow(depth_)
        # plt.savefig(output)
        np.savetxt(output,depth_,delimiter=",")

# 
def create_img_mask(depth_array, threshold):
    """
    takes an image depth_array, with threshold/cutoff value 
    Params: 
        depth_array: np array, of depth values
        threshold: threshold value, between 0 and 1

    Returns: 
        np array of 0s and 1s, for where to turn on or off image pixel

    """
    max_ = np.amax(depth_array)
    thresh_val = threshold*max_
    return np.where(depth_array >= thresh_val, 0, 1) # set anything above the depth to 0, and others to 1

def output_mask_array_folder(folder_name,threshold):
    original_folder_name = folder_name.split("_")[-1] # remove depth_map prefixes from folder name
    output_path = "masks_" + original_folder_name
    if not os.path.exists(output_path): os.makedirs(output_path)
    depths_ = [_ for _ in os.listdir(folder_name) if _.lower().endswith(".csv")] # get csv files

    for depth_ in depths_:
        depth_path = os.path.join(folder_name,depth_)
        depth_arr = np.genfromtxt(depth_path,delimiter=",")
        mask = create_img_mask(depth_arr,threshold)
        original_file_name = depth_.split("_")[-1] #remove other prefixes from file name
        output = "mask_" + original_file_name
        output = os.path.join(output_path,output)
        np.savetxt(output, mask, delimiter=",")









def main():
    args = get_argparse().parse_args()
    # img_ = args.image if args.image else args.folder
    # output_depth_map_image_file(img_,args.model) if args.image else output_depth_map_image_folder(img_,args.model)
    imgs_ = args.folder
    # output_depth_map_array_folder(imgs_,args.model)
    output_mask_array_folder(imgs_,args.threshold)


if __name__ == "__main__":
    main()
