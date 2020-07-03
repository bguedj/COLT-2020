import argparse
import json
import yaml

SESSION_LINK_FMT = 'papers.html?session={0}'

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('zoom', help='input zoom yaml file')
  parser.add_argument('input', help='input calendar json file')
  parser.add_argument('output', help='output json file')
  args = parser.parse_args()

  with open(args.zoom) as f:
    zoom = yaml.safe_load(f)

  events = []
  with open(args.input) as f:
    events = json.load(f)

  for event in events:
    if event['title'].find('Session') >= 0:
      link = SESSION_LINK_FMT.format(event['title'].replace(' ', '+'))
      event_type = 'session'
    elif event['title'].find('Keynote') >= 0:
      link = 'speaker_{0}.html'.format(event['title'][event['title'].find('Keynote') + 8])
      event_type = 'keynote'
    elif event['title'].find('Coffee') >= 0:
      link = 'format.html#coffee'
      event_type = 'coffee'
    elif event['title'].find('Open Problems') >= 0:
      link = SESSION_LINK_FMT.format('Session+OP')
      event_type = 'session'
    elif event['title'].find('Business') >= 0:
      link = 'format.html#business'
      event_type = 'business'
    else:
      link = ''
      event_type = '---'
    event['link'] = link
    event['location'] = link
    event['calendarId'] = event_type

  with open(args.output, 'w') as f:
    json.dump(events,f)


