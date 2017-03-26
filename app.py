from flask import (Flask, render_template, jsonify, redirect, url_for,
            request, make_response, Response, current_app)
from werkzeug.utils import secure_filename
from datetime import datetime
import sys
import httplib
import uuid
sys.stdout = sys.stderr

app = Flask(__name__)

from warp_drive import WarpDrive

WARP_DRIVE = WarpDrive("")

@app.route('/set_cookie')
def cookie_insertion():
    global WARP_DRIVE
    redirect_to_index = redirect('/')
    response = make_response(redirect_to_index )
    directory_sheet_id = WARP_DRIVE.add_spreadsheet()
    WARP_DRIVE = WarpDrive(directory_sheet_id)
    response.set_cookie('directory_sheet_id',value=directory_sheet_id)
    return response

@app.route('/')
def hello_world():
    global WARP_DRIVE
    if 'directory_sheet_id' not in request.cookies:
        redirect_to_cookie_create = redirect('/set_cookie')
        response = make_response(redirect_to_cookie_create )
        return response
    if WARP_DRIVE.directory_sheet_id == "":
        WARP_DRIVE = WarpDrive(request.cookies["directory_sheet_id"])
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def add_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        now = datetime.now()
        current_time = now.isoformat()
        filename = secure_filename(file.filename)
        data = file.read()
        file_id = uuid.uuid4()

        len_data = len(data)
        len_file = WARP_DRIVE.sizeof_fmt(len_data)
        WARP_DRIVE.add_file(file_id, filename, len(data), current_time, data)
        return success((file_id, filename, len_file, now.strftime('%d/%m/%Y at %I:%M:%S %p')))
    else:
        return error(httplib.BAD_REQUEST, 'No file/bad file')

def allowed_file(filename):
    return '.' in filename

@app.route('/get_file/<file_id>/<file_name>', methods=['GET'])
def get_file(file_id, file_name):
    file_data = WARP_DRIVE.read_file(file_id)

    response = make_response(file_data)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = \
        u"attachment; filename={0}".format(file_name)
    return response

    return success((file_name, file_data))

@app.route('/update_file', methods=['POST'])
def update_file():
    return success('update_file')

@app.route('/delete_file', methods=['POST'])
def delete_file():
    file_id = request.values.get('id')
    WARP_DRIVE.delete_file(file_id)
    return success(file_id)

@app.route('/get_all', methods=['GET'])
def get_all():
    return success(WARP_DRIVE.list_files())

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
