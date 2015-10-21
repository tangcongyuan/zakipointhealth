#!/usr/bin/env python
import os, csv, sys, random, pdb
from optparse import OptionParser
from optparse import Option, OptionValueError
VERSION = '0.1.0'

import bio_settings
def analyze_file(filename, outfile, p2k, k2p):
    i = 0
    keys = []
    mask = []
    copy = []
    
    with open(filename) as csv_file:
        for line in csv.reader(csv_file, dialect="excel"):
            if i == 1:
                all_items = list(line)
                print all_items
                for item in bio_settings.key_cols:
                    keys.append(all_items.index(item))
                for item in bio_settings.mask_cols:
                    mask.append(all_items.index(item))
                for item in all_items:
                    copy_items = [itm for itm in bio_settings.all_cols if itm not in (bio_settings.mask_cols.keys()+bio_settings.key_cols)]
                    if item in [itm for itm in copy_items]:
                        copy.append(all_items.index(item))
                print keys
                print mask
                print copy
                outfile.writerow(['UID']+[line[w] for w in sorted(copy+mask)])

            elif i > 1:
                params = []
                for k in keys:
                    if k in mask:
                        try:
                            params.append(bio_settings.get_value(bio_settings.all_cols[k], line[k]))
                        except ValueError:
                            params.append('')
                    else:
                        params.append(line[k].lower())
                try:
                    key_string = '|'.join(params)
                except:
                    pdb.set_trace()
                    pass
                if len(key_string) < len(keys):
                    continue
                md5 = bio_settings.md5(key_string)
                p2k[key_string] = md5
                k2p[md5] = key_string
                outfile.writerow([md5]+[(line[w] if w in copy else bio_settings.mask_cell(bio_settings.all_cols[w], line[w])) for w in sorted(copy+mask)])

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
    description = """Scan biometrics files"""
    parser = OptionParser(option_class=MultipleOption,
                          usage='usage: %prog biom_file, biom_file, ...',
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
