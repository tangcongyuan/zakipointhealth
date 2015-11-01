import csv
import json

def process_file(input_file):
    input_data = csv.DictReader(open(input_file))
    output = []
    for row in input_data:
        output.append(row)
      
    return output
    
