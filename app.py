

from flask import Flask,render_template, jsonify, make_response, request
import os
from pyzbar import pyzbar
from PIL import Image

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('collect.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/postData', methods=["POST","GET"])
def postData():
    return {"h":"i"}


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
    