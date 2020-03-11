import requests
from bs4 import BeautifulSoup
from urllib import parse
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request is being made to host')

session = requests.Session()

response = session.get(
    'https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_lgn', verify=False)
soup = BeautifulSoup(response.text, "html.parser")
inputs = soup.find_all('input')
params = {}
for x in inputs:
    params[x['name']] = x['value']

params['SCREEN_WIDTH.DUMMY.MENSYS.1'] = '1920'
params['SCREEN_HEIGHT.DUMMY.MENSYS.1'] = '1080'
params['MUA_CODE.DUMMY.MENSYS.1'] = 'bpen8455'
params['PASSWORD.DUMMY.MENSYS.1'] = '0123Asdf'

response = session.post(
    url="https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_lgn", data=params, verify=False)

soup = BeautifulSoup(response.text, "html.parser")
inputs = soup.find('input', attrs={'name':'HREF.DUMMY.MENSYS.1'})

mainURL = "https://sydneystudent.sydney.edu.au/sitsvision/wrd/"+inputs['value']

#Main Page
response = session.get(mainURL, verify = False)
soup = BeautifulSoup(response.text, "html.parser")
#msgTitle = soup.find_all('h2', attrs={"class":"sv-panel-title"})[1].string.replace('\n',"").strip()
#msgInfo = soup.find('div',attrs={"class":"sv-form-additional-info sv-help-block sv-small"}).string.replace('\n',"").strip()
hrefs = {}
hrefs['home'] = soup.find('a', attrs={'id':'HOME'})['href']
hrefs['requests'] = soup.find('a', attrs={'id':'SMAPRLST'})['href']
hrefs['details'] = soup.find('a', attrs={'id':'SM_STUPOR02'})['href']
hrefs['residency'] = soup.find('a', attrs={'id':'SM_STUPOR03'})['href']
hrefs['course'] = soup.find('a', attrs={'id':'SMSTUPOR01'})['href']
hrefs['units'] = soup.find('a', attrs={'id':'USSTUPOR01'})['href']
hrefs['assessments'] = soup.find('a', attrs={'id':'ASSTUPOR01'})['href']
hrefs['enrolment'] = soup.find('a', attrs={'id':'ENSTUPOR01'})['href']
hrefs['results'] = soup.find('a', attrs={'id':'RESULTS'})['href']
hrefs['finance'] = soup.find('a', attrs={'id':'FNSAM02'})['href']
hrefs['otherFinance'] = soup.find('a', attrs={'id':'FMFUNDS01'})['href']
hrefs['messages'] = soup.find('a', attrs={'class':'sv-list-group-item sv-list-group-item-overflow'})['href']
hrefs['logout'] = soup.find('a', attrs={'target':'_self'})['href']