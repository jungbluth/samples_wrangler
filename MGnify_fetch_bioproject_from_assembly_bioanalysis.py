#!/usr/bin/env python3

# input list file with links to MGnify analyses: e.g. https://www.ebi.ac.uk/metagenomics/api/v1/assemblies/SAMN02954284/analyses
# output list of bioproject study IDs (e.g., MGYS00000496, ...)

import sys, os, re, time
import json, requests
from pprint import pprint

def main():
  # biome = 'root:Environmental:Terrestrial:Soil'
  listfile=sys.argv[1]
  biome=sys.argv[2]
  file1 = open(listfile, 'r') 
  count = 0
  data=[]

  while True: 
    count += 1
    line = file1.readline() 
    if not line: 
      break
    data.append(fetch_data(line, data))
    time.sleep(5) # try not to get blocked
  write_data_to_list(biome, data)
  file1.close() 

def fetch_data(url, data):
  headers = {'Accept': 'application/json'}
  result=None
  print("url is {}".format(url))
  result = send_request_return_json_data(url, headers)
  data = result['data'][0]['relationships']['study']['data']['id']
  return data

def send_request_return_json_data(url, headers):
  r = requests.get(url, headers=headers)
  result=r.json()
  return result

def write_data_to_list(biome, data):
  biome = biome.replace(":", "_")
  fileout = biome + '_bioproject.list'
  with open(fileout, 'w') as f:
    for item in data:
        f.write("%s\n" % item)

if __name__ == "__main__":
  main()