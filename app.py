from flask import Flask, render_template
from wtforms import StringField, SubmitField

from maxdiff import MaxDiffRater

app = Flask(__name__)

@app.route('/')
def index():
    mdr = MaxDiffRater()
    sample = mdr.get_sample()
    
    return render_template('index.html', sample=sample["items"].values)
