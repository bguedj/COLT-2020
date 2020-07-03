#!/usr/bin/env python

import argparse
import csv
import yaml

def format_name(s):
  parts = s.split(', ')
  if len(parts) > 1:
    return '{0} {1}'.format(parts[1],parts[0])
  else:
    return s

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('zoom', help='input zoom yaml file')
  parser.add_argument('input', help='input file')
  parser.add_argument('slideslive', help='slideslive file')
  parser.add_argument('output', help='output file')
  args = parser.parse_args()

  with open(args.zoom) as f:
    zoom = yaml.safe_load(f)

  fieldnames = ['UID', 'title', 'authors', 'abstract', 'keywords', 'session', 'slideslive_1', 'slideslive_2', 'zoom_1', 'zoom_2', 'position_1', 'position_2']
  rows = {}
  sessions = {}
  with open(args.input) as f:
    # morn,eve,cmtid,tzgroup,ET_cluster,PT_cluster,EU_cluster,Paper Title,Abstract,Primary Contact Author Name,Primary Contact Author Email,Authors,Author Names,Author Emails,Primary Subject Area,Secondary Subject Areas,timezone
    reader = csv.DictReader(f)
    for row in reader:
      uid = row['cmtid']
      morn_session = 'Session ' + row['morn']
      eve_session = 'Session ' + row['eve']
      newrow = {
          'UID': uid,
          'title': row['Paper Title'],
          'authors': '|'.join(format_name(s.replace('*','')) for s in row['Author Names'].split('; ')),
          'abstract': row['Abstract'].replace('\n', '\\n'),
          'keywords': '|'.join([row['Primary Subject Area']] + row['Secondary Subject Areas'].split('; ')),
          'session': '|'.join(sorted([morn_session,eve_session])),
          }
      rows[uid] = newrow
      if sessions.get(morn_session) != None:
        sessions[morn_session].append(newrow)
      else:
        sessions[morn_session] = [newrow]
      if sessions.get(eve_session) != None:
        sessions[eve_session].append(newrow)
      else:
        sessions[eve_session] = [newrow]

  for session, events in sessions.items():
    i = 0
    for paper in events:
      paper_sessions = paper['session'].split('|')
      if paper_sessions[0] == session:
        paper['zoom_1'] = zoom['posters'][i]
        paper['position_1'] = i+1
      elif paper_sessions[1] == session:
        paper['zoom_2'] = zoom['posters'][i]
        paper['position_2'] = i+1
      else:
        raise Error('oops')
      i = i + 1

  with open(args.slideslive) as f:
    reader = csv.DictReader(f)
    for row in reader:
      uid = row['unique ID']
      track = row['Organizer track name']
      if track == 'Open Problems':
        continue
      if 'Short' in track:
        rows[uid]['slideslive_1'] = row['SlidesLive link']
      else:
        rows[uid]['slideslive_2'] = row['SlidesLive link']

  with open(args.output, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for uid, row in rows.items():
      writer.writerow(row)

