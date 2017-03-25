from flask import Flask, render_template, jsonify, redirect, url_for, request
from werkzeug.utils import secure_filename
from datetime import datetime
import sys
import httplib
sys.stdout = sys.stderr

app = Flask(__name__)

@app.route('/')
def hello_world():
  return render_template('index.html')

def _pr(strin):
    print(strin)

@app.route('/upload_file', methods=['POST'])
def add_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        now = datetime.now()
        filename = secure_filename(file.filename)
        _pr('-------filename-------')
        _pr(filename)
        _pr('-------time-------')
        _pr(now.isoformat())
        _pr('-------file-------')
        _pr(file.read())

        return success('file read')
    else:
        return error(httplib.BAD_REQUEST, 'No file/bad file')


def allowed_file(filename):
    return '.' in filename

@app.route('/get_file', methods=['POST'])
def get_file():
    print 'get_file'

@app.route('/update_file', methods=['POST'])
def update_file():
    print 'update_file'

@app.route('/delete_file', methods=['POST'])
def delete_file():
    print 'delete_file'

@app.route('/get_all', methods=['GET'])
def get_all():
    print 'get_all'

def success(data):
    if not isinstance(data, dict):
        results = dict(data=data)
    else:
        results = data
    return jsonify(**results)


def error(code, message):
    response = jsonify(code=code, message=message)
    response.status_code = code
    return response

if __name__ == "__main__":
    app.run(debug=True)
