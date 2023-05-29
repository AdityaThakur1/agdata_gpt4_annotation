import torch
import torchvision
import clip
import numpy as np
import pickle
import time
import torchvision.datasets as datasets
from PIL import Image
from tarimagefolder import TarImageFolder
import subprocess
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor
import torchvision.transforms as transforms

# define the custom collate function
def my_collate(batch):
    # get the maximum height and width of the images in the batch
    max_height = max([img.shape[1] for img, _ in batch])
    max_width = max([img.shape[2] for img, _ in batch])
    
    # create a tensor to hold the padded images
    padded_imgs = torch.zeros(len(batch), 3, max_height, max_width)
    
    # create a tensor to hold the labels
    labels = torch.tensor([label for _, label in batch])
    
    # copy the images into the padded tensor
    for i, (img, _) in enumerate(batch):
        height, width = img.shape[1], img.shape[2]
        padded_imgs[i, :, :height, :width] = img
    
    return padded_imgs, labels

# # create a dataset
# dataset = INaturalist2021(root='/path/to/inaturalist2021', transform=ToTensor())

# # create a dataloader with the custom collate function
# dataloader = DataLoader(dataset, batch_size=32, collate_fn=my_collate)

print("All libraries loaded")
# Load the iNaturalist 2021 dataset
start_time = time.time()
def _convert_image_to_rgb(image):
    return image.convert("RGB")
train_transform = transforms.Compose([
        transforms.Resize(224, interpolation=Image.BICUBIC),
        transforms.CenterCrop(224),
        _convert_image_to_rgb,
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),])
# read the archive
dataset = TarImageFolder('inaturalist_2021/val.tar.gz',root_in_archive='val',transform=train_transform)
print("T:", (time.time() - start_time), "sec - Dataset downloaded")

# Create a data loader with batch size 64
#trainloader = torch.utils.data.DataLoader(train_dataset, batch_size=16)
BATCH_SIZE=2
loader = DataLoader(dataset, batch_size=BATCH_SIZE)

# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
print("cuda") if device == "cuda" else print("cpu")
model, preprocess = clip.load("ViT-B/32", device=device)
print("T:", (time.time() - start_time), "sec - Model loaded")

# Generate embeddings for the training set
train_embeddings = []
idx = 0
for (image, label) in loader:
    # batched_images = []
    # print("processing batch")
    # for i in range(BATCH_SIZE):
    #     pil_image = torchvision.transforms.ToPILImage()(image[i])
    #     img_tensor = preprocess(pil_image).unsqueeze(0).to(device)
    #     batched_images.append(img_tensor)
    # batched_tensor = torch.stack(batched_images)
    # print("Batched images processed")

    #batched_tensor=preprocess(image).unsqueeze(0).to(device)
    image = image.to(device)

    with torch.no_grad():
        embed = model.encode_image(image).squeeze(0).cpu().numpy()
    train_embeddings.append(embed)
    if idx%100 == 0:
        print("T:", (time.time() - start_time), "sec - ", idx , "image embeddings created")
        output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,memory.free', '--format=csv'])
        print(f"GPU usage: {output.decode('utf-8')}")
        print(len(train_embeddings))
    idx += 1

print("T:", (time.time() - start_time), "sec - All Embeddings created")

# Open a file for writing
with open('inat_embeddings_all_val.pkl', 'wb') as f:
    # Write the list to the file using pickle
    pickle.dump(train_embeddings, f)

print("T:", (time.time() - start_time), "sec - Embeddings saved")