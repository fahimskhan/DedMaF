import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Parse():
    def __init__(self, filename):
        self.filename = filename
        self.connect()
        self.readOutput()

    def connect(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('/home/rfeldman/viscoturbulence/file_manager/client_secret.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open("viscoTurb_test").sheet1
        return self.sheet

    def readOutput(self):
        output_file = open(self.filename, 'r').readlines()
        last = len(output_file)
        output = (output_file[last-5:last-1])
        self.finalArr = []
        for i in output:
            lastColon = i.rfind(':')
            final = i[lastColon+1:].strip()
            self.finalArr.append(final)
        return self.finalArr

    def updateSheet(self):
        lastIndex = len(self.connect().get_all_values())
        cell_list = self.sheet.range('M{}'.format(lastIndex)+':'+'Q{}'.format(lastIndex))
        for i in range(0, len(cell_list)-1):
            cell_list[i].value = self.finalArr[i]

        self.sheet.update_cells(cell_list)

#connect()
# print(readOutput())
parser = Parse('slurm-1922.out')
parser.updateSheet()
