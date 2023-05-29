import requests
import os

url = 'https://ml-inat-competition-datasets.s3.amazonaws.com/2021/val.tar.gz'

os.mkdir(inaturalist_2021)
filename = 'inaturalist_2021/val.tar.gz'
filename = 'inaturalist_2021/2021_train.tgz'

# Download the file with streaming
response = requests.get(url, stream=True)

# Check if the response was successful
if response.status_code == 200:
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
    print(f"File downloaded as {filename}")
else:
    print(f"Failed to download file. Status code: {response.status_code}")