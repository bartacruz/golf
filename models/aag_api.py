
import json
import requests
import base64

#root_api = 'http://aag-web-test.tecnocode.net/api/supplier'
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

def do_get(action):
    rurl = '%s%s' % (root_api,action)
    auth = get_auth()
    r = requests.get(rurl,headers={'Authorization':auth})
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
    #print(r.json())
    return r.json()[0]

def get_handicap(handicap_index):
    handicap = round(handicap_index * (course_slope/113)+(course_rating-course_par))
    return handicap
