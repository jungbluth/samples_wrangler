#!/usr/bin/env python3

import sys, os, re
import json, requests
from pprint import pprint

def main():
  study=sys.argv[1]
  base_url='https://www.ebi.ac.uk/metagenomics/api/v1/'
  (analyses_data, samples_data)=prepare_data(study, base_url)
  run=prepare_download(analyses_data, base_url, study)
  (samples, headers)=parse_samples(samples_data, run)
  print_samples(samples, headers)

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
  analyses_url=prepare_url(base_url, 'analyses', study)
  samples_url=prepare_url(base_url, 'samples', study)
  if not os.path.isdir(study):
    os.mkdir(study)
  analyses_data=get_data(analyses_url, f'{study}/analyses.json')
  samples_data=get_data(samples_url, f'{study}/samples.json')
  return (analyses_data, samples_data)

def prepare_download(analyses_data, base_url, target):
  run={}
  print("analyses_data is {}".format(analyses_data))
  for analysis in analyses_data:
    analysis_id=analysis['id']
    print("analysis_id is {}".format(analysis_id))
    downloads=[];
    downloads_url=prepare_url(base_url, 'downloads', analysis_id)
    print("downloads_url is {}".format(downloads_url))
    downloads_data=get_data(downloads_url)
    print("downloads_data is {}".format(downloads_data))
    for dl in downloads_data:
      url=dl['links']['self']
      if re.search(r'FASTA_[0-9]*\.fasta(\.gz)?$', url, re.IGNORECASE) \
      or re.search(r'_FASTA_nt_reads\.fasta(\.gz)?$', url, re.IGNORECASE) \
      or re.search(r'_FASTA\.fasta(\.gz)?$', url, re.IGNORECASE):
        downloads.append(url)
      print("length of downloads is {}".format(len(downloads)))
      # if len(downloads) != 3:
      #   continue
      sample_id=analysis['relationships']['sample']['data']['id']
      print("sample_id is {}".format(sample_id))
      #run[sample_id]=analysis['relationships']['run']['data']['id']
      for dl in downloads:
        print("dl and target are {} and {}".format(dl, target))
        download_data(dl, target) 
  return run
  
def parse_samples(samples_data, run):
  data={}
  headers=[]

  def add_data(id, key, value):
    if key not in headers:
      headers.append(key)
    if not data.get(id):
      data[id]={}
    data[id][key]='' if value is None else value
    return
  
  for sample in samples_data:
    sample_id=sample['id']
    if not (sample.get('attributes') and run.get(sample_id)):
      continue
    add_data(sample_id, 'id', sample_id)
    for k, v in sample['attributes'].items():
      if k == 'sample-metadata':
        for meta in v:
          add_data(sample_id, meta['key'], meta['value'])
      else:
        add_data(sample_id, k ,v)
    add_data(sample_id, 'run', run[sample_id])
  return (data, headers)
    
def print_samples(samples, headers):
  print("\t".join(headers))
  for sample in samples.values():
    values=list(map(lambda x: sample[x], headers))
    print("\t".join(values))
  return

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

def download_data(url, target=None):
  if target is None:
    target=os.getcwd()
  name=url.rsplit('/', 1)[1]
  target=os.path.join(target, name)
  if not os.path.isfile(target):
    r=requests.get(url)
    with open(target, 'wb') as outfile:
      outfile.write(r.content)

if __name__ == "__main__":
  main()