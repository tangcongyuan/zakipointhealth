#!/usr/bin/env python
import os, csv, sys, random, pdb
from optparse import OptionParser
from optparse import Option, OptionValueError
VERSION = '0.1.0'

import claim_settings
def analyze_file(filename, outfile, p2k, k2p):
    i = 0
    keys = []
    mask = []
    copy = []
    
    with open(filename) as csv_file:
        for line in csv.reader(csv_file, dialect="excel"):
            if i == 0:
                all_items = list(line)
                print all_items
                for item in all_items:
                    if item in claim_settings.key_cols:
                        keys.append(all_items.index(item))
                    if item in claim_settings.mask_cols:
                        mask.append(all_items.index(item))
                    copy_items = [itm for itm in claim_settings.all_cols if itm not in (claim_settings.mask_cols.keys()+claim_settings.key_cols)]
                    if item in [itm for itm in copy_items]:
                        copy.append(all_items.index(item))
                print keys
                print mask
                print copy
                outfile.writerow(['UID']+[line[w] for w in sorted(copy+mask)])

            elif i >= 1:
                params = []
                for k in keys:
                    if k in mask:
                        try:
                            params.append(claim_settings.get_value(claim_settings.all_cols[k], line[k]))
                        except ValueError:
                            params.append('')
                    else:
                        params.append(line[k].lower())
                key_string = '|'.join(params)
                if len(key_string) < len(keys):
                    continue
                md5 = claim_settings.md5(key_string)   # hashlib.md5(key_string).hexdigest()
                p2k[key_string] = md5
                k2p[md5] = key_string
                try:
                    outfile.writerow([md5]+[(line[w] if w in copy else claim_settings.mask_cell(claim_settings.all_cols[w], line[w])) for w in sorted(copy+mask)])
                except:
                    print 'Exception', key_string, line
            i += 1

class MultipleOption(Option):
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            values.ensure_value(dest, []).append(value)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

def main():
    PROG = os.path.basename(os.path.splitext(__file__)[0])
    description = """Scan claims files"""
    parser = OptionParser(option_class=MultipleOption,
                          usage='usage: %prog claims_file, claims_file, ...',
                          version='%s %s' % (PROG, VERSION),
                          description=description)
    if len(sys.argv) == 1:
        parser.parse_args(['--help'])

    args = parser.parse_args()
    p2k = {}
    k2p = {}
    try:
        with open('claimants.csv') as csv_file:
            for line in csv.reader(csv_file, dialect="excel"):
                p2k[line[0]] = line[1]
                k2p[line[1]] = line[0]
    except IOError:
        pass
    for filename in args[1]:
        with open(filename+'_masked.csv', 'wb') as cf:
            outfile = csv.writer(cf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            analyze_file(filename, outfile, p2k, k2p)
            print len(p2k), len(k2p)
    with open('claimants.csv', 'wb') as cf:
        cout = csv.writer(cf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for p in p2k:
            cout.writerow([p, p2k[p]])

if __name__ == '__main__':
    main()
