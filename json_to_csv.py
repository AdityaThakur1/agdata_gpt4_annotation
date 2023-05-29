import json
import csv

json_file_list = ['output/20230525_072652_0/master_data.json','output/20230525_074250_501/master_data.json',\
                  'output/20230525_173734_516/master_data.json', 'output/20230525_174340_1001/master_data.json', \
                  'output/20230525_174347_1501/master_data.json', 'output/20230525_174441_2001/master_data.json',\
                  'output/20230526_085445_2478/master_data.json']

gpt_annotation_dict = {}
for json_file in json_file_list:

    with open(json_file, 'r') as f:
        data1 = json.load(f)
        for sciname in data1:
            if sciname not in gpt_annotation_dict:
                gpt_annotation_dict[sciname] = data1[sciname]

#with open(("2500_master_data.json"), "w") as f:
#    json.dump(gpt_annotation_dict, f)

mapping_family, mapping_order = {}, {}
with open('mapping_order.csv', 'r') as f:
    reader = csv.reader(f)
    for rows in reader:
        mapping_family[rows[1]] = rows[4]
        mapping_order[rows[1]] = rows[3]

with open('insecta_expert_annotations_013123.csv', 'r') as f:
    reader = csv.reader(f)
    expert_annot = {rows[0]: rows[3] for rows in reader}

attr_list = ['ScientificName', 'order', 'family', 'CommonName', 'GPT4_Desc', 'Expert Annotation']
csv_data = []
csv_data.append(attr_list)

for sciname in gpt_annotation_dict:
    csv_line = []
    csv_line.append(sciname)
    csv_line.append(mapping_order.get(sciname))
    csv_line.append(mapping_family.get(sciname))
    csv_line.append(gpt_annotation_dict[sciname].get("CommonName"))
    csv_line.append(gpt_annotation_dict[sciname].get("TextDesc"))
    csv_line.append(expert_annot.get(sciname))
    
    csv_data.append(csv_line)

with open('insecta_gpt4_2500_list.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(csv_data)