from flask import Flask, render_template, jsonify, make_response, request
from car import Car
from pyzbar import pyzbar
from PIL import Image
import os, json

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('collect.html')

@app.route('/results', methods=["GET"])
def results():

    vin = request.args.get('vin', "")
    car = Car(vin)

    ecars=[]
    for id_num in list(json.loads(open('electric-cars.json','r').read())['Electric Cars']):
        ecars.append(Car(id_num,True))

    first=car.find_similar(ecars)
    ecars.remove(first)
    ecars[:0] = [first]

    json_ecars=[]
    ecar_comparisons=[]
    for ecar in ecars:
        ecar_comparisons.append(car.compare(ecar))
        json_ecars.append(ecar.get_dict())

    user_car_json = car.get_JSON()
    electric_cars_json = json.dumps({'ElectricCars':json_ecars}).replace('_','')
    electric_car_comparisons_json = json.dumps({'ElectricCarComparisons':ecar_comparisons}).replace('_','')
    return render_template('results.html',user_car=user_car_json,electric_cars=electric_cars_json,electric_car_comparisons=electric_car_comparisons_json)

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
