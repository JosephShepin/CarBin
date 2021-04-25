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
def postData():
    vin = request.args.get('vin', "")
    #car = Car(vin) 
    #ret='{eletric_cars:['
    #electric_cars = []
    #for id_num in list(json.loads(open('electric-cars.json','r').read())['Electric Cars']):
    #    electric_cars.append(Car(id_num,True))

    #ret=''
    #for ecar in electric_cars:
    #    ret+=ecar.__str__()+'<br><br><br>'
    #return ret

    #return render_template('results.html',results=car)
    car = Car(vin).get_all_comparison(Car('0', True))
    return render_template('results.html',results=json.dumps(car))

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

