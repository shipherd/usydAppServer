import requests
from bs4 import BeautifulSoup
from urllib import parse
import warnings
import json
import helper
import time


class GetAllData:
    def __isTimeStampValid(self):
        now = time.time()
        period = 60.0*15.0  # 60 secs times 15 mins
        if (now - self.timeStamp) > period:
            return False
        return True

    def __getJMSG(self, code, msg, hash):
        dic = {"code": code, "msg": msg, "token": hash}
        retJson = json.dumps(dic)
        return retJson

    def __init__(self):
        self.timeStamp = 0
        self.session = requests.Session()
        self.mainURL = ""
        self.hrefs = {}
        warnings.filterwarnings(
            'ignore', message='Unverified HTTPS request is being made to host')

    def login(self, unikey, pw):

        try:
            response = self.session.get(
                'https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_lgn', verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            inputs = soup.find_all('input')
            if inputs == None:
                raise Exception("No inputs found")
        except:
            return self.__getJMSG(helper.ERROR_NETWORK, "Network Error", 0)
        params = {}
        for x in inputs:
            params[x['name']] = x['value']

        params['SCREEN_WIDTH.DUMMY.MENSYS.1'] = '1920'
        params['SCREEN_HEIGHT.DUMMY.MENSYS.1'] = '1080'
        params['MUA_CODE.DUMMY.MENSYS.1'] = unikey
        params['PASSWORD.DUMMY.MENSYS.1'] = pw

        try:
            response = self.session.post(
                url="https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_lgn", data=params, verify=False)
        except:
            return self.__getJMSG(helper.ERROR_NETWORK, "Network Error", 0)
        soup = BeautifulSoup(response.text, "html.parser")
        inputs = soup.find('input', attrs={'name': 'HREF.DUMMY.MENSYS.1'})

        if inputs == None:
            # unikey or pw is wrong
            return self.__getJMSG(helper.ERROR_UNIKEY_OR_PW, "Login Error", 0)
        self.mainURL = "https://sydneystudent.sydney.edu.au/sitsvision/wrd/" + \
            inputs['value']

        self.timeStamp = time.time()

        return self.__getJMSG(helper.ERROR_SUCCESS, "Login Succeed", self.__hash__())

    def getMain(self):
       # return print(self.session.cookies)
        if not self.__isTimeStampValid():
            return self.__getJMSG(helper.ERROR_SESSION_EXPIRED, "Session Expired", self.__hash__())
        response = self.session.get(self.mainURL, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        msgTitle = soup.find_all(
            'h2', attrs={"class": "sv-panel-title"})[1].string.replace('\n', "").strip()
        msgInfo = soup.find('div', attrs={
                            "class": "sv-form-additional-info sv-help-block sv-small"}).string.replace('\n', "").strip()
        retJson = self.__getJMSG(helper.ERROR_SUCCESS, '{"title":"%s", "msg":"%s"}' % (
            msgTitle, msgInfo), self.__hash__())

        self.hrefs['base'] = 'https://sydneystudent.sydney.edu.au/sitsvision/wrd/'
        self.hrefs['home'] = soup.find('a', attrs={'id': 'HOME'})['href']
        self.hrefs['requests'] = soup.find('a', attrs={'id': 'SMAPRLST'})['href']
        self.hrefs['details'] = soup.find('a', attrs={'id': 'SM_STUPOR02'})['href']
        self.hrefs['residency'] = soup.find('a', attrs={'id': 'SM_STUPOR03'})['href']
        self.hrefs['course'] = soup.find('a', attrs={'id': 'SMSTUPOR01'})['href']
        self.hrefs['units'] = soup.find('a', attrs={'id': 'USSTUPOR01'})['href']
        self.hrefs['assessments'] = soup.find('a', attrs={'id': 'ASSTUPOR01'})['href']
        self.hrefs['enrolment'] = soup.find('a', attrs={'id': 'ENSTUPOR01'})['href']
        self.hrefs['results'] = soup.find('a', attrs={'id': 'RESULTS'})['href']
        self.hrefs['finance'] = soup.find('a', attrs={'id': 'FNSAM02'})['href']
        self.hrefs['otherFinance'] = soup.find('a', attrs={'id': 'FMFUNDS01'})['href']
        self.hrefs['messages'] = soup.find('a', attrs={'class': 'sv-list-group-item sv-list-group-item-overflow'})['href']
        self.hrefs['logout'] = soup.find('a', attrs={'target': '_self'})['href']

        return retJson
