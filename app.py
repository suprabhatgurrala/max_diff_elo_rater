from flask import Flask, render_template, request
from wtforms import StringField, SubmitField

from maxdiff import MaxDiffRater

app = Flask(__name__)

mdr = MaxDiffRater()

@app.route('/')
def index():
    sample = mdr.get_sample()

    best = request.args.get("best")
    worst = request.args.get("worst")
    
    if best is not None and worst is not None:
        mdr.submit_results(sample.index, best, worst)

    return render_template('index.html', sample=sample["items"])

@app.route('/results')
def results():
    df = mdr.elo_ratings.sort_values(["elo", "matches"], ascending=False)

    return render_template('results.html', table=df.to_html(classes=["table", "table-dark", "table-hover"], index=False))
