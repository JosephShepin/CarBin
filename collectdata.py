#get either user info, or VIN
import requests,json
def collect_data(id: str):
    #url = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/'
    #post_fields = {'format': 'json', 'data':'JTJZK1BA1D2009651'}
    #url = 'https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getTrims&'
    #r = requests.post(url, data=post_fields)
    url = 'https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getModel&model=11459'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    print(r)
    pass


if __name__ == '__main__':
    collect_data('JTJZK1BA1D2009651')