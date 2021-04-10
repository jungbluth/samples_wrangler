#!/usr/bin/env python3

# modified from MGnify_fetch_bioproject_metadata.py

import sys, os, re
import json, requests
from pprint import pprint


def main():
  study=sys.argv[1]
  base_url='https://www.ebi.ac.uk/metagenomics/api/v1/'
  (samples_data)=prepare_data(study, base_url)

def prepare_url(base_url, type, id):
  url=None;
  if type == 'analyses':
    url=base_url + f'studies/{id}/analyses'
  elif type == 'samples':
    url=base_url + f'studies/{id}/samples'
  elif type == 'downloads':
    url=base_url + f'analyses/{id}/downloads'
  return url

def prepare_data(study, base_url):
  samples_url=prepare_url(base_url, 'samples', study)
  if not os.path.isdir(study):
    os.mkdir(study)
  samples_data=get_data(samples_url, f'{study}/samples.json')
  return (samples_data)

def get_data(url, target=None):
  data=None
  if target and os.path.isfile(target):
    with open(target, 'r') as infile:
      content=infile.read()
      data=json.loads(content)
  else:
    data=_get_data(url)
    if target is not None:
      with open(target, 'w') as outfile:
        json.dump(data, outfile)
  return data

def _get_data(url):
  data=[]
  headers = {'Accept': 'application/json'}
  result=None
  while url is not None:
    r = requests.get(url, headers=headers)
    result=r.json()
    if type(result['data']) == 'str':
      data.append(result['data'])
    else:
      data.extend(result['data'])
    url=result['links'] and result['links']['next'] or None
  return data

if __name__ == "__main__":
  main()
