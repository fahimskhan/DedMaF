import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

logging.basicConfig(filename='connection.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)

class Parse():
    def __init__(self, filename):
        self.filename = filename
        self.connect()
        self.readOutput()

    def connect(self):
        logging.debug('establishing connection')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('../../file_manager/client_secret.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open("viscoTurb_test").sheet1
        self.lastIndex = len(self.sheet.get_all_values())
        return self.sheet

    def readOutput(self):
        output_file = open(self.filename, 'r').readlines()
        last = len(output_file)
        output = (output_file[last-12:last-8])
        self.finalArr = []
        for i in output:
            lastColon = i.rfind(':')
            final = i[lastColon+1:].strip()
            self.finalArr.append(final)
        first = self.finalArr[0].split(' ')
        del self.finalArr[0]
        for j in first:
            if j[0].isdigit():
                self.finalArr.insert(0,j)
        del self.finalArr[-2]
        print(self.finalArr)
        return self.finalArr

    def updateSheet(self):
        cell_list = self.sheet.range('M{}'.format(self.lastIndex)+':'+'Q{}'.format(self.lastIndex))
        for i in range(0, len(cell_list)):
            cell_list[i].value = self.finalArr[i]

        self.sheet.update_cells(cell_list)

parser = Parse('slurm-3044.out')
parser.updateSheet()
