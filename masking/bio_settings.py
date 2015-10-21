#!/user/bin/env python
import datetime, base64, hashlib, pdb
all_cols = ["","User ID","First Name","Last Name","Gender","DOB","Member Status","Member Substatus","Coach First Name","Coach Last Name","Coaching Group","HRA Date","HRA Status","HRA Configuration","Questionnaire Complete","Biometrics Complete","Biometrics Verified","Wellness Score","Biometric Score","Height (ft in)","Weight (lbs)","BMI (in)","Waist (in)","Hip (in)","Neck (in)","Body Fat (%)","BP Systolic (mmHg)","BP Diastolic (mmHg)","Total Cholesterol (mg/dL)","Cholesterol Ratio","HDL Cholesterol(mg/dL)","LDL Cholesterol (mg/dL)","Triglycerides (mg/dL)","Fasting Blood Sugar (mg/dL)","Nonfasting Blood Sugar","A1C","Diabetes HbA1C (%)","PSA (ng/dL)","Cotinine"]
key_cols = ["First Name","Last Name","DOB","Gender"]
mask_cols = {'DOB': ['date', '%d %b %Y'], 'Gender': ['gender']}

def get_value(col_name, cell):
    fmt = mask_cols[col_name]
    if fmt[0] == 'date':
        return datetime.datetime.strptime(cell, fmt[1]).date().isoformat()
    elif fmt[0] == 'gender':
        return cell[0].lower()

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

def md5(key_string):
    md5 = hashlib.md5(key_string).hexdigest()
    return base64.urlsafe_b64encode(md5[0:12])
