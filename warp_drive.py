from __future__ import print_function
import httplib2
import os
import unicodedata

import crypt

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from math import *
from dateutil import parser

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

KEY = "PASSWORD"
DIRECTORY_SHEET_ID = "1RNNyvtmW0dbSzVTew_FyoUsfYmQOmvMoNH_FeP_yAn4"
FERNET_CIPHER = crypt.FernetCipher(KEY)

MAX_CELL = 50000
MAX_USABLE_CELL = MAX_CELL - 1 # since we have an escape character at the front
MAX_COLUMNS = 256
MAX_CELLS = 2000000
MAX_ROWS = 7812 # MAX CELLS / MAX COLUMNS

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

class WarpDrive:

    def __init__(self, directory_sheet_id):
        credentials = WarpDrive.get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
        self.sheets_service = service
        self.directory_sheet_id = directory_sheet_id

    # def sizeof_fmt(num, suffix='B'):
    #     for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
    #         if num < 1024.0:
    #             return "%3.1f%s%s" % (num, unit, suffix)
    #         num /= 1024.0
    #         return "%.1f%s%s" % (num, 'Yi', suffix)

    def list_files(self):
        rangeName = 'Sheet1!A1:E'
        result = self.sheets_service.spreadsheets().values().get(spreadsheetId=self.directory_sheet_id, range=rangeName).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
        else:
            fileList = []
            for row in values:
                fileData = {'file_id': WarpDrive.unescape_cell(row[0]),
                         'file_name': WarpDrive.unescape_cell(row[1]),
                         'size': WarpDrive.unescape_cell(row[2]),
                         'date': parser.parse(WarpDrive.unescape_cell(row[3])).strftime('%d/%m/%Y at %I:%M:%S %p'),
                         'data_sheet_id': WarpDrive.unescape_cell(row[4])}

                fileList.append(fileData)
            return fileList

    def add_file(self, fileid, filename, size, date, data):
        data_sheet_id = self.add_spreadsheet()
        self.create_directory_entry(fileid, filename, size, date, data_sheet_id)
        self.write_data(data_sheet_id, data)

    def add_spreadsheet(self):
        spreadsheet_body = { }
        request = self.sheets_service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        return response['spreadsheetId']

    def create_directory_entry(self, file_id, file_name, size, date, data_sheet_id):
        range_name = 'Sheet1!A1:E'
        value_input_option = 'RAW'
        insert_data_option = 'INSERT_ROWS'
        # [fileid, filename, size, date, dataSpreadsheetId]
        fileRow = [
            WarpDrive.escape_cell(file_id),
            WarpDrive.escape_cell(file_name),
            WarpDrive.escape_cell(size),
            WarpDrive.escape_cell(date),
            WarpDrive.escape_cell(data_sheet_id)
        ]
        values = [
            fileRow
        ]
        value_range_body = {
            'values': values
        }
        request = self.sheets_service.spreadsheets().values().append(
            spreadsheetId=self.directory_sheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=value_range_body
        )
        response = request.execute()

    def write_data(self, data_sheet_id, data):
        encrypted_data = FERNET_CIPHER.encrypt(data)
        totalDataCells = int(ceil(float(len(encrypted_data)) / float(MAX_USABLE_CELL)))

        file_row = []
        for i in range(totalDataCells):
            current_cell = encrypted_data[:MAX_USABLE_CELL]
            file_row.append(WarpDrive.escape_cell(current_cell))
            encrypted_data = encrypted_data[MAX_USABLE_CELL:]
            if i % 256 is 0 and i is not 0:
                self.write_row(data_sheet_id, file_row)
                file_row = []
        # write the last row, if it wasnt a length of 256
        self.write_row(data_sheet_id, file_row)

    def write_row(self, data_sheet_id, row_data):
        # expecting rowData to be a list of string. each string with a length of 50000 or less
        # the entire list being of length 256 or less.
        # each string is escaped with a `
        range_name = 'Sheet1!A1:ZZZ'
        value_input_option = 'RAW'
        insert_data_option = 'INSERT_ROWS'
        values = [
            row_data
        ]
        value_range_body = {
            'values': values
        }
        request = self.sheets_service.spreadsheets().values().append(
            spreadsheetId=data_sheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=value_range_body
        )
        response = request.execute()

    def read_file(self, file_id):
        row = self.file_id_to_row(file_id)
        return self.read_data(row['data_sheet_id'])

    def file_id_to_row(self, file_id):
        fileEntries = self.list_files()
        return [element for element in fileEntries if element['file_id'] == file_id][0]

    def read_data(self, data_sheet_id):
        joined_data = ""
        for row in range(1, MAX_ROWS):
            is_data, data = self.read_row(data_sheet_id, row)
            if not is_data:
                return FERNET_CIPHER.decrypt(joined_data)
            joined_data += data
        return FERNET_CIPHER.decrypt(joined_data)

    def read_row(self, data_sheet_id, row):
        rangeName = 'Sheet1!' + "A" + str(row) + ":" + str(row)
        result = self.sheets_service.spreadsheets().values().get(spreadsheetId=data_sheet_id, range=rangeName).execute()
        values = result.get('values', [])

        if not values:
            return False, ""
        else:
            for row in values:
                joined_data = ""
                for cell in row:
                    cell_data = WarpDrive.unescape_cell(cell)
                    joined_data = joined_data + cell_data
                return True, joined_data

    def delete_file(self, file_id):
        range_name = 'Sheet1!A1:E'
        result = self.sheets_service.spreadsheets().values().get(spreadsheetId=self.directory_sheet_id, range=range_name).execute()
        values = result.get('values', [])
        current_row = 1
        for row in values:
            if WarpDrive.unescape_cell(row[0]) == file_id:
                return self.delete_file_entry(current_row)
            current_row += 1

    def delete_file_entry(self, row):
        ignored, row_data = self.read_row(self.directory_sheet_id, row)
        directory_sheet_id = row_data[4]
        self.delete_row(row)
        # delete_drive_file(dataSpreadsheetId)

    def delete_row(self, row):
        range_name = 'Sheet1!' + "A" + str(row) + ":" + str(row)
        clear_values_request_body = { }
        requests = []
        requests.append({
            'deleteDimension': {
                'range': {
                    "sheetId": 0,
                    "dimension": "ROWS",
                    "startIndex": row - 1,
                    "endIndex": row
                }
            }
        })
        body = { 'requests': requests }
        request = self.sheets_service.spreadsheets().batchUpdate(spreadsheetId=self.directory_sheet_id, body=body)
        response = request.execute()

    # def delete_drive_file(dataSpreadsheetId):
    #     service.files().delete(fileId=dataSpreadsheetId).execute()

    @staticmethod
    def get_credentials():
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    @staticmethod
    def unescape_cell(cell):
        # assert cell[0] is "`", "cell that you're trying to unescape isn't escaped!"
        cell_data = cell[1:]
        normalized_cell_data = unicodedata.normalize('NFKD', cell_data).encode('ascii','ignore')
        return normalized_cell_data

    @staticmethod
    def escape_cell(data):
        # assert data length is less or equal to MAX_USABLE_CELL
        return "`" + str(data)
