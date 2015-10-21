Masking
=======

A set of python scripts for loading data.

Data Ingestion
--------------

Convert the incoming Excel files to CSV after removing spaces from their filenames.
[xls2csv](https://github.com/hempalex/xls2csv/blob/master/xls2csv.py) converts older `.xls` files to CSV.
[xlsx2csv](https://github.com/dilshod/xlsx2csv/blob/master/xlsx2csv.py) converts `.xlsx` files.

```shell
sudo cp ~hsirx/upload_files_here/"Test City CR 2012 Biometric Data.xls" Biometrics2012.xls
xls2csv.py -s 2 Biometrics2012.xls csvs/Biometrics2012.csv

sudo cp ~hsirx/upload_files_here/"Test City CR 2013 Biometric Data.xls" Biometrics2013.xls
xls2csv.py -s 2 Biometrics2013.xls csvs/Biometrics2013.csv

xlsx2csv.py -s 2 Claims2012.xlsx csvs/Claims2012.csv

```
etc.

Clean up the coarse character anomalies. Those ^M things have to be entered as ^V^M.
Remove spurious `new line`s, replace ^Ms by new lines, remove leading blanks, replace multiple white spaces with a single space.
```shell
cat ~/hsirx/csvs/Bio*13.csv | tr '\n' ' ' | tr '' '\n' | sed 's/^ *//g' | sed 's/  / /g' > bio13.csv
cat ~/hsirx/csvs/Bio*14.csv | tr '\n' ' ' | tr '' '\n' | sed 's/^ *//g' | sed 's/  / /g' > bio14.csv
```
etc. The Claims files are pretty clean already.

Process the claims files
```shell
claim_scan.py Claims2014.csv
```
and also process the biometrics files
```shell
bio_scan.py bio14.csv
bio_scan.py bio13.csv
bio_scan.py bio12.csv

```

The files are all translated and a reverse mapping file `claimants.csv` is produced as a side effect.

See the comments in the python files for more details about what the `*_scan.py` and `*_settings.py` files do.

More to do
----------

`claim_scan.py` and `bio_scan.py` have very similar architectures. We should combine them into one.
