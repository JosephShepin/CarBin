import sys, requests, json, re
from datetime import date

class Car:
    def __init__(self, id: str, is_electric: bool = False, is_new: bool = False, id_is_plate: bool = False):
        self._is_electric = is_electric
        if (is_electric):
            data = self.get_electric_data(id)
        else:
            data = self.get_gas_data(id, id_is_plate)
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
        self._range           = data['range']
        self._city_mileage    = data['city_mileage']
        self._highway_mileage = data['highway_mileage']
        self._image           = data['image']

        if not is_new:
                self._price['number'] *= .86 ** (date.today().year - self._year)


    def get_gas_data(self, vin: str, is_plate: bool = False):
        data = Car.fetch_carxse(vin, is_plate)
        data.update(self.fetch_carqueryapi(data['attributes']['make'], data['attributes']['model'], data['attributes']['year'], data['attributes']['trim']))
        city_mileage    = float(data['attributes']['city_mileage'].split(' ', 1)[0])
        highway_mileage = float(data['attributes']['highway_mileage'].split(' ', 1)[0])
        #45% highway 55% city
        average_mileage = 1 / (.55 * (1 / city_mileage) + .45 * (1 / highway_mileage))
        range = average_mileage * float(data['attributes']['fuel_capacity'].split(' ', 1)[0])
        range_units = data['attributes']['city_mileage'].split(' ', 1)[1].split('/', 1)[0]
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
                'number'    : Car.kilometers_per_hour_to_miles_per_hour(float(data['model_top_speed_kph'])),
                'units'     : 'miles/hour'
            },
            'torque'            : {
                'number'    : Car.newton_meters_to_foot_pounds(float(data['model_engine_torque_nm'])),
                'units'     : 'footpounds'
            },
            'horsepower'        : {
                'number'    : float(data['model_engine_power_ps']),
                'units'     : 'horsepower'
            },
            'acceleration'      : {
                'number'    : float(data['model_0_to_100_kph']),
                'units'     : '100 km/h/s'
            },
            'range'     : {
                'number'    : range,
                'units'     : range_units
            },
            'city_mileage'      : {
                'number'    : city_mileage,
                'units'     : str(data['attributes']['city_mileage'].split(' ', 1)[1])
            },
            'highway_mileage'   : {
                'number'    : highway_mileage,
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
                'number'    : Car.kilometers_per_hour_to_miles_per_hour(float(data['Top Speed'])),
                'units'     : 'miles/hour'
            },
            'torque'            : {
                'number'    : Car.newton_meters_to_foot_pounds(float(data['Mean Torque'])),
                'units'     : 'footpounds'
            },
            'horsepower'        : {
                'number'    : float(data['Mean Horsepower']),
                'units'     : 'horsepower'
            },
            'acceleration'      : {
                'number'    : float(data['Avg Acceleration']),
                'units'     : '60 miles/h/s'
            },
            'range'     : {
                'number'    : float(data['Mean Range']),
                'units'     : 'miles'
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
            'price'           : self.calculate_percent_change(other._price['number'], self._price['number']),
            'top_speed'       : self.calculate_percent_change(other._top_speed['number'], self._top_speed['number']),
            'torque'          : self.calculate_percent_change(other._torque['number'], self._torque['number']),
            'horsepower'      : self.calculate_percent_change(other._horsepower['number'], self._horsepower['number']),
            'acceleration'    : self.calculate_percent_change(other._acceleration['number'], self._acceleration['number']),
            'range'           : self.calculate_percent_change(other._range['number'], self._range['number']),
            'city_mileage'    : self.calculate_percent_change(other._city_mileage['number'], self._city_mileage['number']),
            'highway_mileage' : self.calculate_percent_change(other._highway_mileage['number'], self._highway_mileage['number']),
        }

    def find_similar(self, other_cars : list):
        similar = other_cars[0]
        for car in other_cars:
            if Car.fuzzy_string_match(self._type, similar._type):
                if Car.fuzzy_string_match(self._type, car._type):
                    if abs(car._price['number'] - self._price['number']) < abs(similar._price['number'] - self._price['number']):
                        similar = car
            elif abs(car._price['number'] - self._price['number']) < abs(similar._price['number'] - self._price['number']):
                similar = car
        return similar

    def calculate_average_mileage(self):
        return 1 / (.55 * (1 / self._city_mileage) + .45 * (1 / self._highway_mileage))

    def calculate_emissions(self):
        emission = 0
        if self._is_electric:
            emission = 13.76 / calculate_average_mileage()
        else:
            emission = 5.4805 / calculate_average_mileage()
        return {
            'number' : emission,
            'units'  : 'kilogram/kilometer'
        }

    def calculate_annual_cost(self):
        cost = 0
        if self._is_electric:
            cost = 57915 / calculate_average_mileage()
        else:
            cost = 40500 / calculate_average_mileage()
        return {
            'number' : cost,
            'units'  : 'kilogram/kilometer'
        }

    def get_emissions_over_time(self, years, is_new = True):
        emission = 0.0
        emission_change = self.calculate_emissions()
        emissions_over_time = {}
        for i in range(years):
            emissions_over_time[str(date.today().year + years)] = emission
            emission += emission_change
        return emissions_over_time

    def get_cost_over_time(self, years, is_new = True):
        cost = 0.0
        cost_change = self.calculate_annual_cost()
        costs_over_time = {}
        for i in range(years):
            costns_over_time[str(date.today().year + years)] = cost
            costn += cost_change
        return costs_over_time

    @staticmethod
    def fetch_carxse(vin: str, is_plate: bool = False):
        if is_plate:
            url = f'http://api.carsxe.com/platedecoder?key=rnldxnjyx_s9pe9t3ov_kyb2nnr21&plate={vin}&state=MD&format=json'
            r = requests.get(url)
            vin = json.loads(r.text)['vin']
        url = 'https://storage.googleapis.com/car-switch/respoonse.json'
        #url =  f' http://api.carsxe.com/specs?key=rnldxnjyx_s9pe9t3ov_kyb2nnr21&vin={vin}'
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
        # url = f"http://api.carsxe.com/images?key=rnldxnjyx_s9pe9t3ov_kyb2nnr21&make={make}&model={model}"
        return 'https://media.cntraveler.com/photos/57fea9ec8584f8cd20e65f15/16:9/w_1600%2Cc_limit/Aerial-One%26OnlyReethiRah-Maldives-CRHotel.jpg'
        # r = requests.get(url)
        # return json.loads(r.text)["images"][0]["link"]

    @staticmethod
    def fuzzy_string_match(str1: str, str2: str):
        not_word_pattern = re.compile('\W')
        str1 = re.sub(not_word_pattern, '', str1)
        str2 = re.sub(not_word_pattern, '', str2)
        return str1.lower() == str2.lower()

    @staticmethod
    def calculate_percent_change(x: float,y: float):
        return -100 * (1 - x / y)

    @staticmethod
    def newton_meters_to_foot_pounds(nm: float):
        return nm * 0.73756

    @staticmethod
    def kilometers_per_hour_to_miles_per_hour(kmph: float):
        return kmph * 0.6213712

    def get_dict(self):
        return {
            "make"            : self._make,
            "model"           : self._model,
            "year"            : self._year,
            "trim"            : self._trim,
            "style"           : self._style,
            "type"            : self._type,
            "fuel_type"       : self._fuel_type,
            "price"           : self._price,
            "top_speed"       : self._top_speed,
            "torque"          : self._torque,
            "horsepower"      : self._horsepower,
            "acceleration"    : self._acceleration,
            "range"           : self._range,
            "city_mileage"    : self._city_mileage,
            "highway_mileage" : self._highway_mileage,
            "image"           : self._image,
        }

    def get_JSON(self):
        return json.dumps(self.get_dict()).replace('_', '')

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
Range: {self._range['number']} ({self._range['units']})
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
