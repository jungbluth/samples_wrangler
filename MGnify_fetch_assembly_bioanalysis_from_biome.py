#!/usr/bin/env python3

# input biome (e.g., root:Environmental:Terrestrial:Soil)
# output list of assembly accession IDs (e.g., SAMN02954284, ERZ483455, ...)

import sys, os, re
import json, requests
from pprint import pprint

def main():
  # biome = 'root:Environmental:Terrestrial:Soil'
  biome=sys.argv[1]
  (front_url, back_url) = prep_url(biome)
  (data,links)=fetch_data(front_url, back_url)
  write_data_to_list(biome, "assembly_id_", data)
  write_data_to_list(biome, "assembly_id_links_", links)

def prep_url(biome):
  base_url = 'https://www.ebi.ac.uk/metagenomics/api/v1/assemblies?'
  front_url = base_url + 'lineage=' + biome + '&page=' #experiment_type=metagenomic
  back_url = '&page_size=100'
  return front_url, back_url

def fetch_data(front_url, back_url):
  data=[]
  links=[]
  headers = {'Accept': 'application/json'}
  result=None
  # url = https://www.ebi.ac.uk/metagenomics/api/v1/biomes/root:Environmental:Terrestrial:Soil/studies?page=1&page_size=100
  url = front_url + '1' + back_url
  # first data pull required to get number of pages
  result = send_request_return_json_data(url, headers)
  num_pages = result['meta']['pagination']['pages']
  for i in range(num_pages):
    if i == 0: # first page already retrieved
      print("url is {}".format(url))
      for j in range(len(result['data'])):
        data.append(result['data'][j]['id'])
        links.append(result['data'][j]['relationships']['analyses']['links']['related'])
    else:
      url = front_url + str(1 + i) + back_url
      result = send_request_return_json_data(url, headers)
      print("url is {}".format(url))
      for k in range(len(result['data'])):
        data.append(result['data'][k]['id'])
        links.append(result['data'][k]['relationships']['analyses']['links']['related'])
  return data, links

def send_request_return_json_data(url, headers):
  r = requests.get(url, headers=headers)
  result=r.json()
  return result

def write_data_to_list(biome, filename, data):
  biome = biome.replace(":", "_")
  fileout = filename + biome + '.list'
  with open(fileout, 'w') as f:
    for item in data:
        f.write("%s\n" % item)

if __name__ == "__main__":
  main()