

from config import Config


url=Config.LOCAL_URL
url = url+'/trade'
last_trade_date = requests.get(url=url)

print (last_trade_date)