# pylint: disable=global-statement,redefined-outer-name
import argparse
import csv
import glob
import json
import os

import yaml
from flask import Flask, jsonify, redirect, render_template, send_from_directory
from flask_frozen import Freezer
from flaskext.markdown import Markdown

site_data = {}
by_uid = {}


def main(site_data_path):
    global site_data, extra_files
    extra_files = ["README.md"]
    # Load all for your sitedata one time.
    for f in glob.glob(site_data_path + "/*"):
        extra_files.append(f)
        name, typ = f.split("/")[-1].split(".")
        if typ == "json":
            site_data[name] = json.load(open(f))
        elif typ in {"csv", "tsv"}:
            site_data[name] = list(csv.DictReader(open(f)))
        elif typ == "yml":
            site_data[name] = yaml.load(open(f).read(), Loader=yaml.SafeLoader)

    for typ in ["papers", "speakers", "open_problems", "pdfs"]:
        by_uid[typ] = {}
        for p in site_data[typ]:
            by_uid[typ][p["UID"]] = p

    print("Data Successfully Loaded")
    return extra_files


# ------------- SERVER CODE -------------------->

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)
markdown = Markdown(app)

# MAIN PAGES


def _data():
    data = {}
    data["config"] = site_data["config"]
    return data


@app.route("/")
def index():
    return redirect("/schedule.html")


# TOP LEVEL PAGES


# @app.route("/index.html")
# def home():
#     data = _data()
#     data["readme"] = open("README.md").read()
#     data["committee"] = site_data["committee"]["committee"]
#     return render_template("index.html", **data)


#@app.route("/about.html")
#def about():
#    data = _data()
#    data["FAQ"] = site_data["faq"]["FAQ"]
#    return render_template("about.html", **data)


@app.route("/papers.html")
def papers():
    data = _data()
    data["zoom"] = site_data["zoom"]
    # data["papers"] = site_data["papers"]
    return render_template("papers.html", **data)


#@app.route("/paper_vis.html")
#def paper_vis():
#    data = _data()
#    return render_template("papers_vis.html", **data)


@app.route("/schedule.html")
def schedule():
    data = _data()
    data["zoom"] = site_data["zoom"]
    data["day"] = {
        "speakers": site_data["speakers"],
#        "highlighted": [
#            format_paper(by_uid["papers"][h["UID"]]) for h in site_data["highlighted"]
#        ],
    }
    return render_template("schedule.html", **data)

@app.route("/keynotes.html")
def keynotes():
    data = _data()
    data["zoom"] = site_data["zoom"]
    data["day"] = {
        "speakers": site_data["speakers"],
    }
    return render_template("keynotes.html", **data)

@app.route("/format.html")
def conference_format():
    data = _data()
    data["zoom"] = site_data["zoom"]
    return render_template("format.html", **data)

@app.route("/format-shuffle.html")
def conference_format_shuffle():
    data = _data()
    data["zoom"] = site_data["zoom"]
    return render_template("format-shuffle.html", **data)    

@app.route("/news.html")
def news():
    data = _data()
    return render_template("news.html", **data)

#@app.route("/subject_areas.html")
#def subject_areas():
#    data = _data()
#    return render_template("subject_areas.html", **data)

@app.route("/plain.html")
def plain():
    data = _data()
    return render_template("plain.html", **data)

#@app.route("/workshops.html")
#def workshops():
#    data = _data()
#    data["workshops"] = [
#        format_workshop(workshop) for workshop in site_data["workshops"]
#    ]
#    return render_template("workshops.html", **data)


def extract_list_field(v, key):
    value = v.get(key, "")
    if isinstance(value, list):
        return value
    else:
        return value.split("|")


def format_paper(v):
    list_keys = ["authors", "keywords", "session"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "id": v["UID"],
        "forum": v["UID"],
        "content": {
            "title": v["title"],
            "authors": list_fields["authors"],
            "keywords": list_fields["keywords"],
            "abstract": v["abstract"],
            "TLDR": v["abstract"],
            "recs": [],
            "session": list_fields["session"],
            "pdf_url": v.get("pdf_url", ""),
            "slideslive_1": v["slideslive_1"],
            "slideslive_2": v["slideslive_2"],
            "zoom": [v["zoom_1"], v["zoom_2"]],
            "positions": [v["position_1"], v["position_2"]],
        },
    }

def format_open_problem(v):
    list_keys = ["authors"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "id": v["UID"],
        "content": {
            "title": v["title"],
            "authors": list_fields["authors"],
            "pdf_url": v.get("pdf_url", ""),
            "slideslive": v["slideslive"],
            "keywords": ["Open problem"],
            "session": ["Session OP"],
            "positions": [v["position"]],
            "zoom": 0,
         },
     }

def format_workshop(v):
    list_keys = ["authors"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "id": v["UID"],
        "title": v["title"],
        "organizers": list_fields["authors"],
        "abstract": v["abstract"],
    }


# ITEM PAGES


@app.route("/papers/paper_<poster>.html")
def poster(poster):
    uid = poster
    data = _data()
    if 'OP' in uid:
        v = by_uid["open_problems"][uid]
        data["paper"] = format_open_problem(v)
        data["pdfs"] = extract_list_field(by_uid["pdfs"][uid], 'filename')
        return render_template("open_problem.html", **data)
    else:
        v = by_uid["papers"][uid]
        data["paper"] = format_paper(v)
        data["pdfs"] = extract_list_field(by_uid["pdfs"][uid], 'filename')
        return render_template("poster.html", **data)


@app.route("/speaker_<speaker>.html")
def speaker(speaker):
    uid = speaker
    v = by_uid["speakers"][uid]
    data = _data()
    data["zoom"] = site_data["zoom"]
    data["speaker"] = v
    return render_template("speaker.html", **data)


#@app.route("/workshop_<workshop>.html")
#def workshop(workshop):
#    uid = workshop
#    v = by_uid["workshops"][uid]
#    data = _data()
#    data["workshop"] = format_workshop(v)
#    return render_template("workshop.html", **data)


#@app.route("/chat.html")
#def chat():
#    data = _data()
#    return render_template("chat.html", **data)


# FRONT END SERVING


@app.route("/papers.json")
def paper_json():
    json = []
    for v in site_data["papers"]:
        json.append(format_paper(v))
    for v in site_data["open_problems"]:
        json.append(format_open_problem(v))
    return jsonify(json)


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)


@app.route("/serve_<path>.json")
def serve(path):
    return jsonify(site_data[path])


# --------------- DRIVER CODE -------------------------->
# Code to turn it all static


@freezer.register_generator
def generator():

    for paper in site_data["papers"]:
        yield "poster", {"poster": str(paper["UID"])}
    for paper in site_data["open_problems"]:
        yield "poster", {"poster": str(paper["UID"])}
    for speaker in site_data["speakers"]:
        yield "speaker", {"speaker": str(speaker["UID"])}
#    for workshop in site_data["workshops"]:
#        yield "workshop", {"workshop": str(workshop["UID"])}

    for key in site_data:
        yield "serve", {"path": key}


def parse_arguments():
    parser = argparse.ArgumentParser(description="MiniConf Portal Command Line")

    parser.add_argument(
        "--build",
        action="store_true",
        default=False,
        help="Convert the site to static assets",
    )

    parser.add_argument(
        "-b",
        action="store_true",
        default=False,
        dest="build",
        help="Convert the site to static assets",
    )

    parser.add_argument("path", help="Pass the JSON data path and run the server")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()

    site_data_path = args.path
    extra_files = main(site_data_path)

    if args.build:
        freezer.freeze()
        with open("build/.htaccess", "w") as f:
            f.write('ModPagespeedDisallow "*"\n')
            f.write('Options -Indexes\n')
    else:
        debug_val = False
        if os.getenv("FLASK_DEBUG") == "True":
            debug_val = True

        app.run(port=5000, debug=debug_val, extra_files=extra_files)
