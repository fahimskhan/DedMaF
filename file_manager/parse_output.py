import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Parse():
    def __init__(self, filename, output_columns):
        self.filename = filename
        self.cols = output_columns
        self.connect()
        self.readOutput()

    def connect(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('/home/fkhan/simulation_builder/file_manager/client_secret.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open("viscoTurb_test").sheet1
        return self.sheet

    def readOutput(self):
        output_file = open(self.filename, 'r').readlines()
        last = len(output_file)
        output = (output_file[last-28:last-24])
        #print(output)
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
        #print(self.finalArr)
        return self.finalArr

    def updateSheet(self):
        lastIndex = len(self.connect().get_all_values())
        cell_list = self.sheet.range('M{}'.format(lastIndex)+':'+'Q{}'.format(lastIndex))
        #print(cell_list)
        if 'dt' in self.cols:
            cell_list[0].value = self.finalArr[0]
        if 'Time' in self.cols:
            cell_list[1].value = self.finalArr[1]
        if 'Step' in self.cols:
            cell_list[2].value = self.finalArr[2]
        if 'Total Ekin' in self.cols:
            cell_list[3].value = self.finalArr[3]
        if 'Total Run Time' in self.cols:
            cell_list[4].value = self.finalArr[4] 
        #for i in range(0, len(cell_list)):
            #cell_list[i].value = self.finalArr[i]

        self.sheet.update_cells(cell_list)

#connect()
# print(readOutput())
parser = Parse('/home/fkhan/simulation_builder/runs/L/slurm-5384.out', ['dt', 'Time', 'Step', 'Total Ekin', 'Total Run Time'])
parser.updateSheet()
