0. Requires python 3.6+, for easy sorting of dictionary.
1. Get login credentials by logging into https://cms.cern.ch/iCMS/analysisadmin/authorinfo?ancode=SUS-20-004 on firefox
2. Install libraries: `pip3 install browser_cookie3 requests requests_html`
3. Run script: `./get_cms_publications.py`

Note some cms papers are special, where author list checking can't be done with nominal method.  
For the below papers, please check if you are the author yourself, and change the `is_author_for_*` flag in the `get_cms_publications.py`
- https://cms-results.web.cern.ch/cms-results/public-results/publications/CMS-00-002/index.html
- https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-12-028/index.html
- https://cms-results.web.cern.ch/cms-results/public-results/publications/CFT-09-025/index.html
- https://cms-results.web.cern.ch/cms-results/public-results/publications/CMS-00-001/index.html
