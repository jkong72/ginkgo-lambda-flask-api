import requests
import config

url = config.Config.LOCAL_URL
url = url+'/trade'
var = requests.get(url).json()

var = var['data']

print(len(var))

print 