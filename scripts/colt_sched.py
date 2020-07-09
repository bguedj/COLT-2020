import argparse
import csv
import datetime
import json
import pytz
import yaml

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('zoom', help='input zoom yaml file')
  parser.add_argument('papers', help='input paper csv file')
  parser.add_argument('problems', help='input open problems csv file')
  parser.add_argument('calendar', help='input calendar json file')
  parser.add_argument('chairs', help='input chairs csv file')
  parser.add_argument('output', help='output html file')
  args = parser.parse_args()

  papers = {}
  sessions = {}
  events = []
  problems = []
  chairs = {}

  in_fmt = "%Y-%m-%d" + "T" + "%H:%M:%S%z"

  with open(args.zoom) as f:
    zoom = yaml.safe_load(f)

  with open(args.papers) as f:
    reader = csv.DictReader(f)
    for paper in reader:
      papers[paper['UID']] = paper
      paper_sessions = paper['session'].split('|')
      session = sessions.get(paper_sessions[0])
      if session == None:
        session = []
        sessions[paper_sessions[0]] = session
      session.append({ 'UID':paper['UID'], 'position':paper['position_1'], 'zoom':paper['zoom_1'] })
      if len(paper_sessions) > 1:
        session = sessions.get(paper_sessions[1])
        if session == None:
          session = []
          sessions[paper_sessions[1]] = session
        session.append({ 'UID':paper['UID'], 'position':paper['position_2'], 'zoom':paper['zoom_2'] })

  with open(args.problems) as f:
    reader = csv.DictReader(f)
    for paper in reader:
      problems.append(paper)

  with open(args.calendar) as f:
    events = json.load(f)

  with open(args.chairs) as f:
    reader = csv.DictReader(f)
    for row in reader:
      chairs[row['UID']] = row['chair']

  events.sort(key=lambda e: e['start'])

  with open(args.output, 'w') as f:
#    print('<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>COLT 2020 Schedule</title>\n</head>\n<body>\n<table border="1">', file=f)
    print('{% set active_page = "(plain schedule)" %}', file=f)
    print('{% set page_title = "The No-Frills Schedule" %}', file=f)
    print('{% extends "base.html" %}', file=f)
    print('{% block content %}', file=f)
    print('<table border="1">', file=f)
    for event in events:
      if event['link'] != '':
        desc = '<a href="{0}"><strong>{1}</strong></a>'.format(event['link'], event['title'])
      else:
        desc = event['title']
      if event['title'].find('Session ') >= 0:
        desc += ' (Session chair: {0})<br />\n<a href="{1}" target="_blank">[Zoom link for plenary]</a>'.format(chairs[event['title']], zoom['plenary'][0])
      elif (event['title'].find('Session ') >= 0) or (event['title'].find('Keynote ') >= 0) or (event['title'].find('Open Problems') >= 0) or (event['title'].find('Business Meeting') >= 0):
        desc += '<br />\n<a href="{0}" target="_blank">[Zoom link for plenary]</a>'.format(zoom['plenary'][0])
      start = datetime.datetime.strptime(event['start'],"%Y-%m-%dT%H:%M:%S%z").astimezone(pytz.timezone('Etc/GMT+12'))
      start_date = start.strftime('%A %Y-%m-%d')
      start_time = start.strftime('%H:%M <a href="https://www.timeanddate.com/time/zones/aoe">AoE</a>')
      print('  <tr><td style="padding: 5px; white-space: nowrap; text-align: right">{0}<br />{1}</td><td style="padding: 5px">{2}</td></tr>\n'.format(start_date, start_time, desc), file=f)
      if event['title'].find('Open Problems') >= 0:
        problems.sort(key=lambda p: p['UID'])
        for paper in problems:
          title = paper['title']
          authors = ', '.join(paper['authors'].split('|'))
          position = paper['position']
          desc = '<a href="papers/paper_{0}.html"><strong>{1}</strong></a><br />{2}'.format(uid, title, authors)
          print('  <tr><td></td><td style="padding: 5px">{0}. {1}</td></tr>\n'.format(position, desc), file=f)
      if event['title'].find('Session ') >= 0:
        session_paper_keys = sessions[event['title']]
        session_paper_keys.sort(key=lambda p: int(p['position']))
        for paper_key in session_paper_keys:
          uid = paper_key['UID']
          position = paper_key['position']
          paper = papers[uid]
          title = paper['title']
          authors = ', '.join(paper['authors'].split('|'))
          zoom_link = paper_key['zoom']
          desc = '<a href="papers/paper_{0}.html"><strong>{1}</strong></a><br />{2}<br /><a href="{3}" target="_blank">[Zoom link for poster session]</a>'.format(uid, title, authors, zoom_link)
          print('  <tr><td></td><td style="padding: 5px">{0}. {1}</td></tr>\n'.format(position, desc), file=f)
    #print('</table>\n</body>\n</html>', file=f)
    print('</table>', file=f)
    print('{% endblock %}', file=f)

