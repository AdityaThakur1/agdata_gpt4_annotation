import os
import requests
import datetime
import argparse
import openai
from time import sleep
import re
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import pickle
import pandas as pd
from collections import defaultdict
from dotenv import load_dotenv
import json
import csv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--pylists', type=bool, default = False, help='Add if you need data in form of python lists as well')
parser.add_argument('--startrow', type=int, default = 0, help='start of row')
parser.add_argument('--endrow', type=int, default = 3000, help='end row')
parser.add_argument('--csv_file', type=str, help='CSV file')

# Parse the arguments
args = parser.parse_args()
pylists = args.pylists

if args.startrow == 0:
    df = pd.read_csv(args.csv_file, nrows=args.endrow)
else:
    df = pd.read_csv(args.csv_file, skiprows=range(1, args.startrow-1) , nrows=args.endrow, header=0)
print (df.size)
print(df.iloc[0])
#print(pylists)
#Starting with some list of names to query
sciNames = df["Scientific Name"].tolist()
commonNames= df["Common Name"].tolist()
order = df["Order"].tolist()
family= df["Family"].tolist()

#Generate a list of queries
queryList = []
errorList = []
for name in sciNames:
    if pylists == True:
        query = name + ' morphological identifying features and then also give the same data in form of two python lists with correct syntax where the first list is attributes and the second list is values.'
    else:
        query = name + ' morphological identifying features'
    queryList.append(query)

master_attribute_dict = defaultdict(int)
master_data = {}
csv_data = []

#Set your API key
openai.api_key = os.environ.get("OPENAI_API_KEY")
# Set your OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Define the API endpoint
endpoint = "https://api.openai.com/v1/chat/completions"

# Define the headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

output_folder = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_"+ str(args.startrow)
os.mkdir("output/" + output_folder )

for idx, q in enumerate(tqdm(queryList)):
    attempts, ext_attempts = 0, 0
    while ext_attempts < 12:
        try:
            while attempts < 10:
                try:
                    # Define the payload
                    payload = {
                        "model": "gpt-4",
                        "messages": [
                            {"role": "user", "content": q}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 750,
                    }
                    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
                    response_json = response.json()
                    break
                except Exception as e:
                    sleep(1)
                    print(e)
                    attempts += 1
            answer = response_json["choices"][0]["message"]["content"].lower()
            print(answer)
            text_desc, attributes, values = [],[],[]
            for line in answer.split("\n"):
                if line == "":
                    #skip empty lines in output
                    continue

                if pylists and (line[:9] == "attribute" or line[:5] == "value"):
                    ls_data = re.findall(r"'(.*?)'", line)
                    #if list elements were in double quotes
                    if(len(ls_data) == 0):
                        ls_data = re.findall(r'"(.*?)"', line)

                    if line[:3] == "att":
                        attributes.extend(ls_data)

                    elif line[:3] =="val":
                        values.extend(ls_data)
                
                else:
                    text_desc.append(line)


            #verify attributes and values are not empty and have same number of entries
            if pylists:
                if (len(attributes) != len(values)) or len(attributes) == 0 or len(values) == 0 or len(text_desc) == 0:
                    errorList.append([sciNames[idx]])
                    print(sciNames[idx], ext_attempts)
                    print(completion)
                    print("--------------------------------------------------------------------")
                    raise TypeError('Not proper values for attr and val')
                else:
                    break
            
            break
    
        except Exception as e:
                sleep(1)
                print(e)
                if(ext_attempts == 11):
                    errorList.append([sciNames[idx]])
                ext_attempts += 1
    
    attr_dict = {}
    attr_dict["CommonName"] = commonNames[idx]
    attr_dict["Order"] = order[idx]
    attr_dict["Family"] = family[idx]
    if pylists:
        for attr, val in zip(attributes, values):
            attr_dict[attr] = val
            master_attribute_dict[attr] += 1
    attr_dict["TextDesc"] = text_desc
    master_data[sciNames[idx]] = attr_dict

    with open(("output/" + output_folder + "/master_data.json"), "w") as f:
        json.dump(master_data, f)

   
# with open((output_folder + "master_data.json"), "w") as f:
#     json.dump(master_data, f)
    
# with open("out_v2/master_attribute.json", "w") as f:
#     json.dump(master_attribute_dict, f)

with open(("output/" + output_folder +  "/error_data.csv"), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(errorList)

# with open('out_v2/master_data.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerows(csv_data)

# master_attribute_csv = []
# for key in master_attribute_dict:
#     ls = [key,master_attribute_dict[key]]
#     master_attribute_csv.append(ls)

# with open('out_v2/master_attr.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerows(master_attribute_csv)