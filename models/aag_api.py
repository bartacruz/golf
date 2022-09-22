
import json
import requests
import base64

#root_web = 'http://aag-web-test.tecnocode.net/api/supplier'

#root_api = 'http://aag-api-test.tecnocode.net/api/supplier' #test
root_api = 'https://aag-api-prod.azurewebsites.net/api/supplier' #prod
user = 'sistema365'
key = 'cdfe3d64-4dfb-412a-8c00-7ce1b95eeca4' #prod
#key = '98ef99fb-a1c7-4d5c-89e0-da2fed98f431' #test
course_rating = 64.8
course_slope = 103
course_par = 68

def get_auth():
    auth_string = '%s:%s' % (user,key)
    #print(auth_string)
    auth = '%s %s' % ('Basic', base64.b64encode(auth_string.encode('ascii')).decode('ascii'))
    #print(auth)
    return auth

def do_get(action, data=None):
    rurl = '%s%s' % (root_api,action)
    auth = get_auth()
    if data:
        r = requests.get(rurl,params=data,headers={'Authorization':auth})    
    else:
        r = requests.get(rurl,headers={'Authorization':auth})
    print(auth)
    print(r.url)
    return r

def do_post(action,data):
    rurl = '%s%s' % (root_api,action)
    print(rurl)    
    auth = get_auth()
    r = requests.post(rurl,data=data, headers={'Content-type':'application/json', 'Authorization':auth})
    return r

def get_enrolled(license):
    data = '[%s]' % license
    action = "/enrolleds"
    r = do_post(action,data)
    print(r.json())
    if r.json():
        return r.json()[0]
    else:
        return False

def get_handicap(handicap_index):
    handicap = round(handicap_index * (course_slope/113)+(course_rating-course_par))
    return handicap

def get_fields():
    action = "/fields"
    r = do_get(action)
    print(r.text)
    #print(r.json())
    return r.json()[0]

def get_tournaments():
    action = "/tournament"
    r = do_get(action)
    print(r.text)
    return r.json()

def get_tournament(tournament_id):
    action = "/tournament"
    r = do_get(action,{'Id':tournament_id})
    return r.json()

def post_tournament(data):
    action = "/tournament"
    r = do_post(action,json.dumps(data))
    return r.json()