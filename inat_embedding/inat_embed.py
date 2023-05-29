import torch
import torchvision
import clip
import numpy as np
import pickle
import time

print("All libraries loaded")
# Load the iNaturalist 2021 dataset
data_dir = 'inaturalist_2021'
start_time = time.time()
#train_dataset = torchvision.datasets.INaturalist(root=data_dir, version='2021_train', download=True)
print("T:", (time.time() - start_time), "sec - Dataset downloaded")

# Create a data loader with batch size 64
#trainloader = torch.utils.data.DataLoader(train_dataset, batch_size=1024, shuffle=True)

# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
print("T:", (time.time() - start_time), "sec - Model loaded")

# Generate embeddings for the training set
train_embeddings = []
for i in range(len(train_dataset)):
    image, _ = train_dataset[i]
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        embed = model.encode_image(image).squeeze(0).cpu().numpy()
    train_embeddings.append(embed)
    if i%1000 == 0:
        print("T:", (time.time() - start_time), "sec || ", i , "image embeddings created") 
    #break

print("T:", (time.time() - start_time), "sec - Embeddings created")

# Open a file for writing
with open('inat_embeddings.pkl', 'wb') as f:
    # Write the list to the file using pickle
    pickle.dump(train_embeddings, f)

print("T:", (time.time() - start_time), "sec - Embeddings saved")