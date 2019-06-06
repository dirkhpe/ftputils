#!/opt/envs/awv/bin/python3

"""
Script to capture indicator filezwaarte - nieuwe berekening from verkeersindicatoren
"""

import datetime
import json
import logging
import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lib import ftp_handler
from lib import info_layer
from lib import my_env

locations = my_env.locations
dagdeel = my_env.dagdeel
dagtype = my_env.dagtype
aggregatieniveau = my_env.aggregatieniveau
voertuigklasse = my_env.voertuigklasse
wegcategorie = my_env.wegcategorie
indicator = my_env.indicator

cfg = my_env.init_env("verkeerscentrum", __file__)
sa = info_layer.SqlAlConn(cfg)
if os.environ.get("http_proxy"):
    os.environ.pop("http_proxy")
if os.environ.get("https_proxy"):
    os.environ.pop("https_proxy")

now = datetime.datetime.now().date()
current_year = int(now.strftime("%Y"))
current_month = int(now.strftime("%m"))
url_starter = "http://indicatoren.verkeerscentrum.be/vc.indicators.web.gui/filezwaarteIndicator/tableData?criteria="
req_dict = dict(
    ra_id=aggregatieniveau["invloedsgebied"],
    dagtype_id=dagtype["werkdag"],
    voertuigklasse=voertuigklasse["alle"],
    wcgroep_id=wegcategorie["hoofrijb en knoop"],
    tableType="month",
    locations=[str(locations[x]) for x in locations]
)
ffn = os.path.join(cfg["Main"]["indic_dir"], cfg["Main"]["fn_filezwaarte"])
fh = open(ffn, "w")
title = "indicatorfiche_id;aantal;jaar;maand;dagdeel;arrondissement"
fh.write(title + "\n")
for year in range(2012, current_year+1):
    for startMonth in [1, 5, 9]:
        rep_date = datetime.date(year, startMonth, 1)
        if rep_date > now:
            break
        req_dict["monthStartYear"] = year
        req_dict["monthEndYear"] = year
        req_dict["startMonth"] = startMonth
        req_dict["endMonth"] = startMonth + 3
        for dd in ["am", "pm"]:
            logging.info("Working on {year} {month} {dd}".format(year=year, month=startMonth, dd=dd))
            req_dict["dagdeel_id"] = dagdeel[dd]
            req_str = json.dumps(req_dict)
            url = "{url_starter}{req_str}".format(url_starter=url_starter, req_str=req_str)
            res = requests.get(url)
            rows = res.json()["rows"]
            for row in rows:
                periode, ra, gem, voort = row["values"]
                if voort:
                    jaar, maand = periode.split("/")
                    if ra == "Rest Vlaanderen":
                        ra = "Andere"
                    resline = "{ind};{aantal};{jaar};{maand};{dagdeel};{arrond}".format(ind=indicator["filezwaarte_nb"],
                                                                                        aantal=voort,
                                                                                        jaar=jaar, maand=int(maand),
                                                                                        dagdeel=dd, arrond=ra)
                    fh.write(resline + "\n")
fh.close()

with open(ffn, 'rb') as fp:
    fc = fp.read()
    if sa.file_update("filezwaarte", fc):
        ftp = ftp_handler.FtpHandler(cfg)
        ftp.load_file(ffn)
        ftp.close_connection()

        gmail_user = cfg['Mail']['gmail_user']
        gmail_pwd = cfg['Mail']['gmail_pwd']
        recipient = cfg['Mail']['recipient']

        msg = MIMEMultipart()
        msg["Subject"] = "Nieuwe publicatie Filezwaarte"
        msg["From"] = gmail_user
        msg["To"] = recipient

        body = "Nieuwe gegevens Filezwaarte gepubliceerd."
        msg.attach(MIMEText(body, 'plain'))

        smtp_server = cfg['Mail']['smtp_server']
        smtp_port = cfg['Mail']['smtp_port']

        if cfg['Mail']['sendOK'] == 'Yes':
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            text = msg.as_string()
            server.sendmail(gmail_user, recipient, text)
            logging.debug("Mail sent!")
            server.quit()
