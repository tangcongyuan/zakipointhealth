#!/user/bin/env python
import datetime, base64, hashlib, pdb
all_cols = ["Certificate Number","Member Number","Incurred Date","Patient First Name","Patient Last Name","Patient Birth Date","Patient Gender Desc","Relationship to Plan Member Desc","CPT Code","CPT Desc","Procedure Code","Procedure Desc","Primary Valid Diagnosis Code","Primary Valid Diagnosis Desc","PBM Brand Name Desc","Place of Service Desc","Provider Name","Claims Settled/Paid Amt"]
key_cols = ["Patient First Name","Patient Last Name","Patient Birth Date","Patient Gender Desc"]
mask_cols = {'Patient Birth Date': ['date', 'flex'], "Patient Gender Desc": ['gender']}

def get_value(col_name, cell):
    fmt = mask_cols[col_name]
    if fmt[0] == 'date':
        if len(cell) == 8:
            flexformat = '%m-%d-%y'
        elif len(cell) == 10:
            flexformat = '%Y-%m-%d'
        else:
            return ''
        # print col_name, cell, len(cell), flexformat
        tmp_date = datetime.datetime.strptime(cell, flexformat).date()
        offset = 100 if tmp_date.year > datetime.date.today().year else 0
        return datetime.date(tmp_date.year - offset, tmp_date.month, tmp_date.day).isoformat()
    elif fmt[0] == 'gender':
        if len(cell):
            return cell[0].lower()
        return ''
    """
    if len(cell) == 8:
        year_in_date = int(cell[6:8])
        year_in_date += 1900 if year_in_date > 15 else 2000
        mnth_in_date = int(cell[0:2])
        date_in_date = int(cell[3:5])
    else:
        year_in_date = int(cell[0:4])
        mnth_in_date = int(cell[5:7])
        date_in_date = int(cell[8:10])
    try:
        return datetime.date(year_in_date, mnth_in_date, date_in_date)
    except ValueError:
        pdb.set_trace()
    """

def mask_cell(col_name, cell):
    fmt = mask_cols[col_name]
    if fmt[0] == 'date':
        try:
            date_iso = get_value(col_name, cell)
            date = datetime.datetime.strptime(date_iso, '%Y-%m-%d').date()
            # first month of the quarter, expressed as two digits
            qmonth = (1+3*int((date.month-1)/3))
            return datetime.date(date.year, qmonth, 1).isoformat()
        except:
            return ''
    elif fmt[0] == 'gender':
        return cell[0]
    else:
        pdb.set_trace()
        return ''

def md5(key_string):
    md5 = hashlib.md5(key_string).hexdigest()
    return base64.urlsafe_b64encode(md5[0:12])
