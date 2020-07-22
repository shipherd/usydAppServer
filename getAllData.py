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
        self.hrefs = {}
        warnings.filterwarnings(
            'ignore', message='Unverified HTTPS request is being made to host')

    def login(self, unikey, pw):

        try:
            soup = self.__getParsedHTMLFromURL(
                'https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_lgn')
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
            return self.__getJMSG(helper.ERROR_UNIKEY_OR_PW, "Incorrect unikey or password", 0)

        self.timeStamp = time.time()

        soup = self.__getParsedHTMLFromURL(
            "https://sydneystudent.sydney.edu.au/sitsvision/wrd/" + inputs['value'])
        self.hrefs['base'] = 'https://sydneystudent.sydney.edu.au/sitsvision/wrd/'
        self.hrefs['home'] = soup.find('a', attrs={'id': 'HOME'})['href']
        ############
        self.hrefs['requests'] = soup.find(
            'a', attrs={'id': 'SMAPRLST'})['href']
        self.hrefs['details'] = soup.find(
            'a', attrs={'id': 'SM_STUPOR02'})['href']
        self.hrefs['residency'] = soup.find(
            'a', attrs={'id': 'SM_STUPOR03'})['href']
        self.hrefs['course'] = soup.find(
            'a', attrs={'id': 'SMSTUPOR01'})['href']
        self.hrefs['units'] = soup.find(
            'a', attrs={'id': 'USSTUPOR01'})['href']
        self.hrefs['assessments'] = soup.find(
            'a', attrs={'id': 'ASSTUPOR01'})['href']
        self.hrefs['enrolment'] = soup.find(
            'a', attrs={'id': 'ENSTUPOR01'})['href']
        self.hrefs['results'] = soup.find('a', attrs={'id': 'RESULTS'})['href']
        self.hrefs['finance'] = soup.find('a', attrs={'id': 'FNSAM02'})['href']
        self.hrefs['otherFinance'] = soup.find(
            'a', attrs={'id': 'FMFUNDS01'})['href']
        self.hrefs['messages'] = soup.find(
            'a', attrs={'class': 'sv-list-group-item sv-list-group-item-overflow'})['href']
        self.hrefs['logout'] = soup.find(
            'a', attrs={'target': '_self'})['href']

        return self.__getJMSG(helper.ERROR_SUCCESS, "Login Succeed", self.__hash__())

    def __getParsedHTMLFromURL(self, URL):
        response = self.session.get(URL, verify=False)
        return BeautifulSoup(response.text, "html.parser")

    def doFunction(self, function):
        if not self.__isTimeStampValid():
            return self.__getJMSG(helper.ERROR_SESSION_EXPIRED, "Session Expired", self.__hash__())

        if function == helper.FUNC_NOTICE:  # Please beware that notice is in Home page
            soup = self.__getParsedHTMLFromURL(
                self.hrefs['base']+self.hrefs['home'])
            msgTitle = soup.find_all(
                'h2', attrs={"class": "sv-panel-title"})[1].string.replace('\n', "").strip()
            msgInfo = soup.find('div', attrs={
                                "class": "sv-form-additional-info sv-help-block sv-small"}).string.replace('\n', "").strip()
            retJson = self.__getJMSG(helper.ERROR_SUCCESS, '{"title":"%s", "msg":"%s"}' % (
                msgTitle, msgInfo), self.__hash__())
        elif function == helper.FUNC_RESULT:
            soup = self.__getParsedHTMLFromURL(
                self.hrefs['base']+self.hrefs['assessments'])

            all_a = soup.find_all('a')

            for x in all_a:
                if x.string != None and "View your academic transcript for" in x.string:
                    uri = x['href'].replace('../wrd/', '')
                    soup = self.__getParsedHTMLFromURL(self.hrefs['base']+uri)

                    all_table = soup.find_all(
                        'table', attrs={"class": "sv-table sv-table-striped"})
                    unit_table = all_table[0]
                    average_table = all_table[1]

                    all_tr = unit_table.find_all('tr')

                    headList = [y.string for y in all_tr.pop(0).find_all('th')]
                    unitHead = headList

                    all_td = all_tr.pop().find_all('td')
                    tailMap = {all_td[0].string: int(all_td[1].string)}

                    bodyList = [{headList[i]: x.string.strip(
                    ) if x.string != '\xa0' else 'NA' for i, x in enumerate(y.find_all('td'))} for y in all_tr]

                    unitMap = {"headers": headList,
                               "body": bodyList, "tail": tailMap}

                    all_tr = average_table.find_all('tr')
                    headList = [y.string for y in all_tr.pop(0).find_all('th')]
                    bodyList = [{headList[i]: x.string for i, x in enumerate(
                        y.find_all('td'))} for y in all_tr]

                    # Calc EHIWAM and WAM
                    thesisUnits = [
                        'CSYS5050', 'CSYS5051','AMME5020','AMME5021',
                        'AMME5022','AMME5222','AMME5223','BMET5020',
                        'BMET5021','BMET5022','BMET5222','BMET5223',
                        'CHNG5020','CHNG5021','CHNG5022','CHNG5222',
                        'CHNG5223','CIVL5020','CIVL5021','CIVL5022',
                        'CIVL5222','CIVL5223','ELEC5020','ELEC5021',
                        'ELEC5022','ELEC5222','ELEC5223',
                        #UG Thesis
                        'AMME4111','AMME4112','BMET4111','BMET4112',
                        'CHNG4811','CHNG4812', 'CHNG4802', 'CHNG4806',
                        'CIVL4022', 'CIVL4023', 'ELEC4712','ELEC4713',
                        'AMME4111', 'AMME4112','AMME4111','AMME4112'
                        ]
                    eUpper = 0.0
                    eLower = 0.0
                    sUpper = 0.0
                    sLower = 0.0
                    allUnits = unitMap['body']
                    for x in allUnits:
                        code = x[unitHead[2]]
                        mark = x[unitHead[4]]
                        cp = x[unitHead[4]]

                        if code in thesisUnits:
                            Wi = 8
                        elif code[4]=='2':
                            Wi = 2
                        elif code[4] == '3':
                            Wi = 3
                        elif int(code[4]) >= 4:
                            Wi = 4
                        else:
                            Wi = 0
                        CPi = float(cp if cp != 'NA' else '0.0')
                        Mi = float(mark if mark != 'NA' else '0.0')

                        eUpper += Wi*CPi*Mi
                        eLower += Wi*CPi
                        sUpper += CPi*Mi
                        sLower += CPi

                    EHIWAM = eUpper/eLower
                    WAM = sUpper/sLower

                    averageMap = {"headers:": headList, "body": bodyList, "tail": {
                        "EHIWAM": str(EHIWAM), "WAM": str(WAM)}}
                    resultMap = {"units": unitMap, "averages": averageMap}
                    retJson = self.__getJMSG(
                        helper.ERROR_SUCCESS, json.dumps(resultMap), self.__hash__())
        elif function==helper.FUNC_DETAILS:
            soup = self.__getParsedHTMLFromURL(self.hrefs['base']+self.hrefs['details'])
            sidMSG = soup.find('div',attrs={'class':'sv-list-group'}).find('p').string
            personalInfo ={'sid':sidMSG}
            for x,y in zip(soup.find_all('dt'), soup.find_all('dd')):
                personalInfo[x.text.strip()] = y.text.strip()
            table = soup.find('table',attrs={'class':"sv-table",'data-tablesaw-mode':"stack"})
            headers = [x.string for x in table.find_all('th')]
            body = {headers[i]:k.text.replace('\xa0',' ') for i,k in enumerate(table.find_all('td'))}

            soup = self.__getParsedHTMLFromURL(self.hrefs['base']+self.hrefs['residency'])
            mainDIV = soup.find('div',attrs={'class':'sv-list-group'})
            all_div = mainDIV.find_all('div',attrs={'class':"sv-panel sv-panel-default"})
            all_div.pop(0)
            residency = {}
            for x in all_div:
                title = x.find('h2',attrs={'class':'sv-panel-title'}).text
                tmp = {}
            for y,z in zip(x.find_all('dt'),x.find_all('dd')):
                tmp[y.text.strip()] = z.text.strip()
                residency[title] = tmp
            details = {'person':personalInfo, 'emergency':body, 'residency':residency}
            retJson = self.__getJMSG(helper.ERROR_SUCCESS, json.dumps(details),self.__hash__())
        else:
            retJson = self.__getJMSG(
                helper.ERROR_POST_PARAMS, "Parameters Error", self.__hash__())
        return retJson
