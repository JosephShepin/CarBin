import sys, requests, json, re
from datetime import date

class Car:

    def __init__(self, id: str, is_electric: bool = False, is_new: bool = False):
        self._is_electric = is_electric
        if (is_electric):
            data = self.get_electric_data(id)
        else:
            data = self.get_gas_data(id)
        self._make            = data['make']
        self._model           = data['model']
        self._year            = data['year']
        self._trim            = data['trim']
        self._style           = data['style']
        self._type            = data['type']
        self._fuel_type       = data['fuel_type']
        self._price           = data['price']
        self._top_speed       = data['top_speed']
        self._torque          = data['torque']
        self._horsepower      = data['horsepower']
        self._acceleration    = data['acceleration']
        self._fuel_capacity   = data['fuel_capacity']
        self._city_mileage    = data['city_mileage']
        self._highway_mileage = data['highway_mileage']
        self._image           = data['image']

        if not is_new:
                self._price['number'] *= self._price['number'] * .86 ** (date.today().year - self._year)


    def get_gas_data(self, vin: str):
        data = self.fetch_carxse(vin)
        data.update(self.fetch_carqueryapi(data['attributes']['make'], data['attributes']['model'], data['attributes']['year'], data['attributes']['trim']))
        return {
            'make'              : data['attributes']['make'],
            'model'             : data['attributes']['model'],
            'year'              : int(data['attributes']['year']),
            'trim'              : data['attributes']['trim'],
            'style'             : data['attributes']['style'],
            'type'              : data['model_body'],
            'fuel_type'         : data['attributes']['fuel_type'],
            'price'             : {
                'number'    : float(data['attributes']['manufacturer_suggested_retail_price'].split(' ', 1)[0][1:].replace(',', '')),
                'units'     : str(data['attributes']['manufacturer_suggested_retail_price'].split(' ', 1)[1])
            },
            'top_speed'         : {
                'number'    : float(data['model_top_speed_kph']),
                'units'     : 'kilometers/hour'
            },
            'torque'            : {
                'number'    : float(data['model_engine_torque_nm']),
                'units'     : 'newtonmeters'
            },
            'horsepower'        : {
                'number'    : float(data['model_engine_power_ps']),
                'units'     : 'horsepower'
            },
            'acceleration'      : {
                'number'    : float(data['model_0_to_100_kph']),
                'units'     : '100 km/h/s'
            },
            'fuel_capacity'     : {
                'number'    : float(data['attributes']['fuel_capacity'].split(' ', 1)[0]),
                'units'     : str(data['attributes']['fuel_capacity'].split(' ', 1)[1])
            },
            'city_mileage'      : {
                'number'    : float(data['attributes']['city_mileage'].split(' ', 1)[0]),
                'units'     : str(data['attributes']['city_mileage'].split(' ', 1)[1])
            },
            'highway_mileage'   : {
                'number'    : float(data['attributes']['highway_mileage'].split(' ', 1)[0]),
                'units'     : str(data['attributes']['highway_mileage'].split(' ', 1)[1])
            },
            'image'             : Car.fetch_image(data['attributes']['make'], data['attributes']['model'])
        }

    def get_electric_data(self, num: str):
        data = json.loads(open('electric-cars.json','r').read())['Electric Cars'][num]
        return {
            'make'              : data['Make'],
            'model'             : data['Model'],
            'year'              : int(data['Year']),
            'trim'              : data['Trim'],
            'style'             : 'ELECTRIC',
            'type'              : data['Type'],
            'fuel_type'         : 'ELECTRIC',
            'price'             : {
                'number'    : float(data['MSRP']),
                'units'     : 'USD'
            },
            'top_speed'         : {
                'number'    : float(data['Top Speed']),
                'units'     : 'kilometers/hour'
            },
            'torque'            : {
                'number'    : float(data['Mean Torque']),
                'units'     : 'newtonmeters'
            },
            'horsepower'        : {
                'number'    : float(data['Mean Horsepower']),
                'units'     : 'horsepower'
            },
            'acceleration'      : {
                'number'    : float(data['Avg Acceleration']),
                'units'     : '60 miles/h/s'
            },
            'fuel_capacity'     : {
                'number'    : float(data['Mean Range']),
                'units'     : ''
            },
            'city_mileage'      : {
                'number'    : float(data['MPGeCity']),
                'units'     : 'miles/gallon'
            },
            'highway_mileage'   : {
                'number'    : float(data['MPGeHighway']),
                'units'     : 'miles/gallon'
            },
            'image'             : data['Image']
        }

    def compare(self, other):
        return {
            'images'           : {
                'car 1'  : self._image,
                'car 2'  : self._image
            },
            'price'           : {
                'car 1'  : self._price['number'],
                'car 2'  : other._price['number'],
                'change' : self.calculate_percent_change(other._price['number'], self._price['number']),
            },
            'top_speed'       : {
                'car 1'  : self._top_speed['number'],
                'car 2'  : other._top_speed['number'],
                'change' : self.calculate_percent_change(other._top_speed['number'], self._top_speed['number']),
            },
            'torque'          : {
                'car 1'  : self._torque['number'],
                'car 2'  : other._torque['number'],
                'change' : self.calculate_percent_change(other._torque['number'], self._torque['number']),
            },
            'horsepower'      : {
                'car 1'  : self._horsepower['number'],
                'car 2'  : other._horsepower['number'],
                'change' : self.calculate_percent_change(other._horsepower['number'], self._horsepower['number']),
            },
            'acceleration'    : {
                'car 1'  : self._acceleration['number'],
                'car 2'  : other._acceleration['number'],
                'change' : self.calculate_percent_change(other._acceleration['number'], self._acceleration['number']),
            },
            'fuel_capacity'   : {
                'car 1'  : self._fuel_capacity['number'],
                'car 2'  : other._fuel_capacity['number'],
                'change' : self.calculate_percent_change(other._fuel_capacity['number'], self._fuel_capacity['number']),
            },
            'city_mileage'    : {
                'car 1'  : self._city_mileage['number'],
                'car 2'  : other._city_mileage['number'],
                'change' : self.calculate_percent_change(other._city_mileage['number'], self._city_mileage['number']),
            },
            'highway_mileage' : {
                'car 1'  : self._highway_mileage['number'],
                'car 2'  : other._highway_mileage['number'],
                'change' : self.calculate_percent_change(other._highway_mileage['number'], self._highway_mileage['number']),
            }
        }

    @staticmethod
    def fetch_carxse(vin: str):
        url = 'https://storage.googleapis.com/car-switch/respoonse.json'
        #url =  f'https://api.carsxe.com/specs?key=rnldxnjyx_s9pe9t3ov_kyb2nnr21&vin={vin}
        r = requests.get(url)
        return json.loads(r.text)

    @staticmethod
    def fetch_carqueryapi(make: str, model: str, year: str, trim: str):
        url = f'https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getTrims&make={make}&year={year}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        for entry in json.loads(r.text[2:-2])['Trims']:
            if Car.fuzzy_string_match(entry['model_name'] + entry['model_trim'], model + trim):
                return entry
        return {}

    @staticmethod
    def fetch_image(make: str, model: str):
        url = f"http://api.carsxe.com/images?key=rnldxnjyx_s9pe9t3ov_kyb2nnr21&make={make}&model={model}"
        r = requests.get(url)
        return json.loads(r.text)["images"][0]["link"]

    @staticmethod
    def fuzzy_string_match(str1: str, str2: str):
        not_word_pattern = re.compile('\W')
        str1 = re.sub(not_word_pattern, '', str1)
        str2 = re.sub(not_word_pattern, '', str2)
        return str1.lower() == str2.lower()

    @staticmethod
    def calculate_percent_change(x: float,y: float):
        return 100*(1-x/y)

    def __str__(self):
         return f'''
Make: {self._make}
Model: {self._model}
Year: {self._year}
Trim: {self._trim}
Style: {self._style}
Type: {self._type}
Fuel Type: {self._fuel_type}
Electric: {self._is_electric}
Price: {self._price['number']} ({self._price['units']})
Top Speed: {self._top_speed['number']} ({self._top_speed['units']})
Torque: {self._torque['number']} ({self._torque['units']})
Horsepower: {self._horsepower['number']} ({self._horsepower['units']})
Acceleration: {self._acceleration['number']} ({self._acceleration['units']})
Fuel Capacity: {self._fuel_capacity['number']} ({self._fuel_capacity['units']})
City Mileage: {self._city_mileage['number']} ({self._city_mileage['units']})
Highway Mileage: {self._highway_mileage['number']} ({self._highway_mileage['units']})
'''

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print(f'Usage: {sys.argv[0]} [Your VIN] [Compare Electric Car ID]')
        exit()
    car_gas = Car(sys.argv[1])
    print(car_gas)
    car_elec = Car(sys.argv[2], True)
    print(car_elec)
    print(json.dumps(car_gas.compare(car_elec),indent=2))
