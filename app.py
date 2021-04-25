from flask import Flask, render_template, request, redirect
from car import Car
from licensedetect import get_plate_from_path
#from pyzbar import pyzbar
from PIL import Image
import os, json

UPLOAD_FOLDER = '/home/w1n5t0n/docs/SHS-Hacks-2021/upload'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def main():
    return render_template('collect.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/results', methods=["GET","POST"])
def results():

    if request.args.get('plate', '') != '':
        car = Car(request.args.get('plate', ''),False,False,True)
    elif request.args.get('vin', '') != '':
        car = Car(request.args.get('vin', ''))
    else:
        file = request.files['imgfile']
        path=os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)
        car = Car(get_plate_from_path(path),False,False,True)

    ecars=[]
    for id_num in list(json.loads(open('electric-cars.json','r').read())['Electric Cars']):
        ecars.append(Car(id_num,True))

    first=car.find_similar(ecars)
    ecars.remove(first)
    ecars[:0] = [first]

    json_ecars=[]
    ecar_comparisons=[]
    footprint_time=[]
    cost_time=[]
    for ecar in ecars:
        ecar_comparisons.append(car.compare(ecar))
        json_ecars.append(ecar.get_dict())
        footprint_time.append(ecar.get_emissions_over_time(10))
        cost_time.append(ecar.get_cost_over_time(10,False))

    user_car_json = car.get_JSON()
    electric_cars_json = json.dumps({'ElectricCars':json_ecars}).replace('_','')
    electric_car_comparisons_json = json.dumps({'ElectricCarComparisons':ecar_comparisons}).replace('_','')
    footprint_time = json.dumps(footprint_time)
    cost_time = json.dumps(cost_time)
    user_car_footprint_time = json.dumps(car.get_emissions_over_time(10))
    user_car_cost_time = json.dumps(car.get_cost_over_time(10,False))
    return render_template('results.html',user_car=user_car_json,electric_cars=electric_cars_json,electric_car_comparisons=electric_car_comparisons_json,footprint_time=footprint_time,cost_time=cost_time,user_car_footprint_time=user_car_footprint_time,user_car_cost_time=user_car_cost_time)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        path = os.path.join("./upload", file1.filename)
        file1.save(path)
        info = pyzbar.decode(Image.open(path))
        vin = info[0][0].decode("utf-8")
        os.remove(path)
        return vin


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
