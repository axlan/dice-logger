import logging
import argparse
from datetime import datetime
import os
from pathlib import Path
import sqlite3
import time
import re

from http.server import HTTPServer, SimpleHTTPRequestHandler

import pandas as pd
import plotly.express as px

DB_NAME = "rolls.db"
PORT = 2020

state = {}

start_time_re = re.compile(r'/gen(/([0-9]+))?')

# 192.168.1.110:2020 - list plots
# 192.168.1.110:2020/gen - generate plot for last 24 hours
# 192.168.1.110:2020/gen/1723267912 - generate plot for 8/10/24 (see https://www.unixtimestamp.com/)

class MySimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        m = start_time_re.match(self.path)
        if m is not None:
            if m.group(2):
                end_time = int(m.group(2))
            else:
                end_time = time.time()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output_path = generate_plot(state['output_dir'], end_time -
                                        60*60*24, end_time)
            if output_path == '':
                self.wfile.write(b'No rolls found')
            else:
                self.wfile.write(f'Generated <a href="{output_path.name}">{output_path}</a>'.encode('utf-8'))
        else:
            return super().do_GET()


def generate_plot(output_dir, start_time, end_time):
    db_path = output_dir / DB_NAME
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM rolls WHERE timestamp > {
                           start_time} AND timestamp < {end_time} AND state == 1", con)
    if len(df) == 0:
        return ''

    timestamps = (df["timestamp"] - df["timestamp"].min()) / 60
    timestr = datetime.fromtimestamp(
        df["timestamp"].min()).strftime("%Y-%m-%d")

    fig = px.bar(
        df,
        x=timestamps,
        y="value",
        color="label",
        labels={
            "x": "Game Time (min)",
            "value": "Roll",
        },
        title=f"Roll Report: {timestr}",
    )

    output_path = output_dir / f"rolls_{timestr}.html"
    fig.write_html(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate an html plot of rolls captured by mqtt_logger.py")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path(__file__).absolute().parent / "datadir",
        help="Directory to log to",
    )
    args = parser.parse_args()

    state['output_dir'] = args.output_dir

    os.chdir(args.output_dir)
    try:
        httpd = HTTPServer(('', PORT), MySimpleHTTPRequestHandler)
        print(f"Serving HTTP on http://0.0.0.0:{PORT}/")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
