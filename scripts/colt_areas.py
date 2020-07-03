import argparse
import csv

# extracts subject areas from papers list

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('papers', help='input paper csv file')
  parser.add_argument('output', help='output html file')
  args = parser.parse_args()

  keywords = set()
  with open(args.papers) as f:
    reader = csv.DictReader(f)
    for paper in reader:
      keywords.update(set(paper['keywords'].split('|')))

  with open(args.output, 'w') as f:
    print('{% set active_page = "Subject Areas" %}', file=f)
    print('{% set page_title = "Subject Areas" %}', file=f)
    print('{% extends "base.html" %}', file=f)
    print('{% block content %}', file=f)
    print('<ul>', file=f)
    for keyword in sorted(list(keywords), key=lambda x: x.lower()):
      if keyword != '':
        print('<li><a href="papers.html?filter=area&search={0}">{1}</a></li>'.format(keyword.replace(' ', '+'),keyword), file=f)
    print('{% endblock %}', file=f)

