import web
import json
import helper
from getAllData import GetAllData

objHashMap = {}

def main():
    webapp = web.application(urls,globals())
    webapp.run()

urls = (
    '/','index',
    '/login','login',
    '/do','do'
)

class index:
    def GET(self):
        return '/'

class do:
    def GET(self):
        raise web.SeeOther('/')
    def POST(self):
        try:
            params = web.data()
            dic = json.loads(params)
            print("Client: {} with hash : {} wants to {}".format(web.ctx['ip'], dic['token'], dic['function']))
            token = dic['token']
            func = dic['function']
        except:
            return json.dumps({"code":helper.ERROR_POST_PARAMS,"msg":"Parameters error","token":0})
        try:
            obj = objHashMap[token]
        except:
            return json.dumps({"code":helper.ERROR_OBJ_NOTFOUND,"msg":"Object error","token":0})
        strJson = obj.doFunction(func)
        if json.loads(strJson)['code']==helper.ERROR_SESSION_EXPIRED:
            objHashMap.pop(dic['token'])
        return strJson

class login:
    def GET(self):
        raise web.SeeOther('/')
    def POST(self):
        instance = GetAllData()
        print("Client: {} has connected. Instance hash : {}".format(web.ctx['ip'], instance.__hash__()))
        try:
            params = web.data()
            dic = json.loads(params)
            key = dic['unikey']
            pw = dic['pw']
        except:
            return json.dumps({"code":helper.ERROR_POST_PARAMS,"msg":"Parameters error","token":0})

        objHashMap[instance.__hash__()] = instance
        return instance.login(key,pw)


if __name__ == '__main__':
    main()
