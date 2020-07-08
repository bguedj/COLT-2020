#!/usr/bin/env python

import argparse
import csv
import yaml

rooms = ['Hosts: Coffee Room 1','Hosts: Coffee Room 2','Hosts: Coffee Room 3','Hosts: Coffee Room 4', 'GRAD Student Coffee Room']

def format_name(name):
  return '' if name == 'VOLUNTEER?' else name

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('input', help='coffee break hosts downloaded file')
  parser.add_argument('output', help='output file')
  args = parser.parse_args()

  newrows = {}
  with open(args.input) as f:
    reader = csv.DictReader(f)
    for row in reader:
      uid = row['Prior Session']
      if uid == '':
        continue;
      if uid not in newrows:
        newrows[uid] = {'UID': uid}
        for room in rooms:
          newrows[uid][room] = format_name(row[room])
      else:
        for room in rooms:
          if format_name(row[room]) != '':
            newrows[uid][room] = newrows[uid][room] + ' and ' + format_name(row[room])


  fieldnames = ['UID'] + rooms

  with open(args.output, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for uid, row in newrows.items():
      writer.writerow(row)