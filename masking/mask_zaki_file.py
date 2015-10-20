import sys, csv, pprint, hashlib, datetime
from optparse import OptionParser
from collections import defaultdict

col_name = 'Prv ID'
col_name = 'Claim UID'
col_name = 'Clmnt ID'
line_col_name = 'Line Nbr'

hash_cols = ["Clmnt ID"]
hide_cols = ["Clmnt First Nm","Clmnt Last Nm","Emp SSN"]
mask_cols = ['Clmnt Birth Dt']


def hash_cell(cell):
    return hashlib.md5(cell).hexdigest()

def mask_cell(cell):
    year_at_end = int(cell[-4:])
    year_now = datetime.datetime.now().year
    if (year_at_end > (year_now - 125)) and (year_at_end <= year_now):
        mnth = int(('0'+cell)[-8:][:2])
        # first month of the quarter, expressed as two digits
        qmnth = '%02d'%(1+3*int((mnth-1)/3))
        date = str(year_at_end) + qmnth
    else:
        date = str(cell)[:6]
    return date[:6] + '01'

def mask_file(in_name):
    outname = in_name.replace('.csv', '.xxx.csv')
    with open(in_name, 'rU') as in_file:
        file_reader = csv.reader(in_file, delimiter=',', quotechar='"')
        with open(outname, 'wb') as out_handler:
            fileout = csv.writer(out_handler, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for in_header_row in file_reader:
                print in_header_row
                row_reader = csv.DictReader(in_file, in_header_row)
                out_header_row = [col for col in in_header_row if not col in hide_cols]
                fileout.writerow(out_header_row)
                break

            for in_row in row_reader:
                for cell in hash_cols:
                    in_row[cell] = hash_cell(in_row[cell])
                for cell in mask_cols:
                    in_row[cell] = mask_cell(in_row[cell])
                out_row = [in_row[cell] for cell in out_header_row]
                fileout.writerow(out_row)

if __name__ == "__main__":

    optparser = OptionParser()
    optparser.add_option('-f', '--inputFile',
                         dest='input',
                         help='filename containing csv',
                         default=None)

    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is not None:
            mask_file(options.input)
    else:
            print 'No dataset filename specified, system with exit\n'
            sys.exit('System will exit')

