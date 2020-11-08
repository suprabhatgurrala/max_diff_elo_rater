from flask import Flask, render_template, request

from maxdiff import MaxDiffRater

app = Flask(__name__)

mdr = MaxDiffRater()

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main page, displays a sample of items and allows you to submit best and worst ones.
    """
    if request.method == 'POST':
        sample_ids = request.form.getlist("sample_ids")
        best = request.form.get("best")
        worst = request.form.get("worst")
        mdr.submit_results(sample_ids, best, worst)
    
    sample = mdr.get_sample()
    
    return render_template('index.html', sample=sample["items"])

@app.route('/results')
def results():
    """
    Results page, shows ratings of all items.
    """
    df = mdr.elo_ratings.sort_values(["elo", "matches"], ascending=False)

    return render_template('results.html', table=df.to_html(classes=["table", "table-dark", "table-hover"], index=False))
