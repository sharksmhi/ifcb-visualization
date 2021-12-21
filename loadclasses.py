import argparse
import csv
import datetime
import logging
import pathlib
import re
import sys

import scipy.io as sio


filename_re = re.compile(
    r'D(?P<year>\d{4})'
    r'(?P<month>\d{2})'
    r'(?P<date>\d{2})'
    r'T(?P<hour>\d{2})'
    r'(?P<minute>\d{2})'
    r'(?P<second>\d{2})'
    r'_IFCB(?P<imager_id>\d{3})'
    r'_class_v1.mat'
)

parser = argparse.ArgumentParser(
    description='Load identified classes from matlab file(s)'
)

parser.add_argument('file', help='path to matlab file(s)')
parser.add_argument('-O', '--output', dest='target', help='path to output file')

args = parser.parse_args()

path = pathlib.Path(args.file)

try:
    if args.target == None:
        output = sys.stdout
    else:
        output = open(args.target, 'w')

    csv_writer = csv.writer(output)

    csv_writer.writerow(('Imager ID', 'Sampled at', 'Class'))

    for infile in pathlib.Path(path.parent).glob(path.name):
        name_match = filename_re.fullmatch(infile.name)
    
        if name_match == None:
            logging.warning('Skipping file: %s.' % infile)
            continue
    
        name_attrs = name_match.groupdict()

        sampled_at = datetime.datetime(
            year=int(name_attrs['year']),
            month=int(name_attrs['month']),
            day=int(name_attrs['date']),
            hour=int(name_attrs['hour']),
            minute=int(name_attrs['minute']),
            second= int(name_attrs['second']),
        )
        imager_id = int(name_attrs['imager_id'])

        matlab_content = sio.loadmat(infile, simplify_cells=True)
    
        for identified_class in matlab_content['TBclass']:
            csv_writer.writerow((imager_id, sampled_at, identified_class))

finally:
    if output and output != sys.stdout:
        output.close()
