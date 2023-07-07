#!/usr/bin/env python3.6
import browser_cookie3
import requests
import requests_html
import bs4
import json
import os
import urllib.parse
import re
import datetime

if __name__ == '__main__':
  look_for_new_papers = True
  look_for_if_author = True

  # These are papers that were treated differently. Please check if you are in the author list yourself.
  # https://cms-results.web.cern.ch/cms-results/public-results/publications/CMS-00-002/index.html
  is_author_for_CMS_00_002 = False
  # https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-12-028/index.html
  is_author_for_HIG_12_028 = False
  # https://cms-results.web.cern.ch/cms-results/public-results/publications/CFT-09-025/index.html
  is_author_for_CFT_09_025 = False
  # https://cms-results.web.cern.ch/cms-results/public-results/publications/CMS-00-001/index.html
  is_author_for_CMS_00_001 = False

  cms_paper_filename = 'cms_paper.json'
  author_paper_filename = 'cms_author_paper.json'
  non_author_paper_filename = 'cms_non_author_paper.json'

  # Paper number in http://cms-results.web.cern.ch/cms-results/public-results/publications/CMS/index.html
  first_paper_number = 0 
  #first_paper_number = 1040 # Skip searching for old papers

  # Get all CMS papers
  # cms_paper_dict[an] = {number:, title:, url:, ref:}
  cms_paper_dict = {}
  if os.path.isfile(cms_paper_filename):
    # Load existing json data
    with open(cms_paper_filename) as infile:
      cms_paper_dict = json.load(infile)
    print(f'Loaded {cms_paper_filename}')
  if look_for_new_papers:
    url = 'http://cms-results.web.cern.ch/cms-results/public-results/publications/CMS/index.html'
    print(f'Looking for new papers in {url}')
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.content.decode('UTF-8'), 'html.parser')
    #print(resp.content.decode('UTF-8'))
    # Add additional papers
    for row in soup.find_all('tr'):
      paper_number_info = row.find_all('td', class_="num")
      if len(paper_number_info) == 0: continue # Not a paper
      paper_url_info = row.find('td',class_="status").find('a')
      if paper_url_info == None:  continue # Not published
      paper_an = row.find('td', class_="cadi").find('a').text
      if paper_an in cms_paper_dict: continue # Already searched for
      paper_number = int(paper_number_info[0].text.strip())
      if paper_number < first_paper_number: continue # Skip old papers
      paper_detail_relurl = row.find('td', class_="cadi").find('a').get('href')
      paper_detail_url = urllib.parse.urljoin(url,paper_detail_relurl)
      paper_title = row.find('td', class_="title").text.strip()
      paper_url = paper_url_info.get('href')
      paper_ref = paper_url_info.text.strip()
      cms_paper_dict[paper_an] = {'number': paper_number, 'title': paper_title, 'url': paper_url, 'ref': paper_ref, 'detail_url': paper_detail_url}
      print(f'Added {paper_an} {cms_paper_dict[paper_an]}')
    # Write to json
    with open(cms_paper_filename, 'w') as outfile:
      json.dump(cms_paper_dict, outfile, indent=2)
    print(f'Saved to {cms_paper_filename}')
  
  # Find if I am an author
  # author_paper_dict[an] = {number:, title:, url:, ref:, detail_url:, number_authors:, publish_date:,}
  author_paper_dict = {}
  # Load existing json data
  if os.path.isfile(author_paper_filename):
    with open(author_paper_filename) as infile:
      author_paper_dict = json.load(infile)
    print(f'Loaded {author_paper_filename}')
  # non_author_paper_dict[an] = {number:, title:, url:, ref:}
  non_author_paper_dict = {}
  # Load existing json data
  if os.path.isfile(non_author_paper_filename):
    with open(non_author_paper_filename) as infile:
      non_author_paper_dict = json.load(infile)
    print(f'Loaded {non_author_paper_filename}')
  if look_for_if_author:
    # Find if I am an author, and then get number of authors and publication date
    cookiejar = browser_cookie3.firefox(domain_name='cern.ch')
    for paper_an in cms_paper_dict:
      if paper_an in author_paper_dict: continue # Already searched for this an
      if paper_an in non_author_paper_dict: continue # Already searched for this an
      paper_number = cms_paper_dict[paper_an]['number']
      print(f'[{paper_number}] Checking for authorship of {paper_an}')
      url = f'https://cms.cern.ch/iCMS/analysisadmin/authorinfo?ancode={paper_an}'
      resp = requests.get(url, cookies=cookiejar)
      soup = bs4.BeautifulSoup(resp.content.decode('UTF-8'), 'html.parser')
      is_author = False
      #print(url)
      if paper_an == "CMS-00-002": is_author = is_author_for_CMS_00_002
      elif paper_an == "HIG-12-028": is_author = is_author_for_HIG_12_028
      elif paper_an == "CFT-09-025": is_author = is_author_for_CFT_09_025
      elif paper_an == "CMS-00-001": is_author = is_author_for_CMS_00_001
      elif 'is in the author' in soup.find_all('div')[1].text.strip(): is_author = True
      if not is_author: 
        non_author_paper_dict[paper_an] = cms_paper_dict[paper_an]
        # Write to json. In loop incase something fails.
        with open(non_author_paper_filename, 'w') as outfile:
          json.dump(non_author_paper_dict, outfile, indent=2)
        continue # Not an author
      author_paper_dict[paper_an] = cms_paper_dict[paper_an]
      # Find cds and inspire url in detail_url
      cds_url = ''
      inspire_url = ''
      paper_detail_url = cms_paper_dict[paper_an]['detail_url']
      resp_cms = requests.get(paper_detail_url)
      soup_cms = bs4.BeautifulSoup(resp_cms.content.decode('UTF-8'), 'html.parser')
      #print(resp_cms.content.decode('UTF-8'))
      for link_row in soup_cms.find_all('td', class_='link'):
        for link in link_row.find_all('a'):
          if 'cds' in link.get('href'): cds_url = link.get('href')
          if 'inspirehep' in link.get('href'): inspire_url = link.get('href')
      #print(f'{paper_an} {cds_url} {inspire_url}')
      # Get number of authors from cds
      # Bug fix for detail_url
      if cds_url == 'https://cds.cern.ch/record/2777215':
        cds_url = 'http://cds.cern.ch/record/2777347'
      resp_cds = requests.get(cds_url)
      number_authors = int(re.findall(r'\d+',re.findall("Show all.*$",resp_cds.content.decode('UTF-8'),re.MULTILINE)[0])[0])
      author_paper_dict[paper_an]['number_authors'] = number_authors
      # Get publication date from inspire
      #print(inspire_url)
      publish_date = ''
      for iTrial in range(10):
        try:
          session = requests_html.HTMLSession()
          resp_inspire = session.get(inspire_url)
          resp_inspire.html.render()
          #print(f'html: {resp_inspire.html.text}')
          publish_date = re.findall(r'Published:\ .*$', resp_inspire.html.text, re.MULTILINE)[0].strip('Published:').strip()
          break
        except:
          print(f'Trying again to get publication date from {inspire_url}')
      if publish_date == '': 
        print(f'Error in getting publish date in {inspire_url}')
        break
      author_paper_dict[paper_an]['publish_date'] = publish_date
      print(f'Added {paper_an} {author_paper_dict[paper_an]}')
      # Write to json. In loop incase something fails.
      with open(author_paper_filename, 'w') as outfile:
        json.dump(author_paper_dict, outfile, indent=2)
    print(f'Saved to {author_paper_filename}')
    print(f'Saved to {non_author_paper_filename}')

  # Sort dict by publication date
  date_reverse = False
  author_paper_dict = {k: v for k, v in sorted(author_paper_dict.items(), key=lambda item: datetime.datetime.strptime(item[1]['publish_date'], '%b %d, %Y'), reverse=date_reverse)}

  # Print information pretty
  paper_number = 1
  for paper_an in author_paper_dict:
    paper_title = author_paper_dict[paper_an]['title']
    paper_ref = author_paper_dict[paper_an]['ref']
    paper_number_authors = author_paper_dict[paper_an]['number_authors']
    paper_date = author_paper_dict[paper_an]['publish_date']
    paper_date_kor = datetime.datetime.strptime(paper_date, '%b %d, %Y').strftime('%Y/%m/%d')
    print(f'{paper_number:03} {paper_date_kor} {paper_ref} {paper_title} 김재박외 {paper_number_authors}명')
    paper_number += 1
