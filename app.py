from flask import Flask,render_template, jsonify, make_response

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    