from flask import Flask, request, render_template, Markup, url_for, g
import json
import pymongo as mdb

app = Flask(__name__)

@app.context_processor
def add_vars_to_context():
    return dict(site_title="AmazonFeatures")

######################################
# DATABASE                           #
######################################

def connect_db():
    conn = mdb.MongoClient()
    db = conn.app
    coll = db.products
    return (conn, coll)

@app.before_request
def before_request():
    g.db_conn, g.db_coll = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db_conn'):
        g.db_conn.close()

######################################
# VIEWS                              #
######################################

# home
@app.route('/')
def index():
    return render_template('index.html',
                            page_title="Home")

# about
@app.route('/about')
def about():
    contents = """
        <p>AmazonFeatures is a feature-based sentiment extractor. Using the text from over 83 million Amazon product reviews, it attempts to identify the most important positive and negative features for individual products.</p>
        <p><b>Why?</b> Because product reviews contain valuable information, but reading through them can be time consuming and tedious. AmazonFeatures sifts through the noise and identifies the pros and cons of a product for you.<p>
        <p>For more about how AmazonFeatures works, please <a href='https://amazonfeatures.robdalton.me/data' >see here</a>.</p>
        <p>For more about Robert Dalton, please <a href='https://robdalton.me'>see here</a>.</p>
   """
    return render_template('page.html',
                            page_title="About",
                            contents=Markup(contents))

# data
@app.route('/data')
def data():
    contents = """

    """
    return render_template('page.html',
                            page_title="Data",
                            contents=Markup(contents))

# search results
@app.route('/search', methods=['GET', 'POST'])
def search():
    # create index
    g.db_coll.create_index([("title", "text")])

    # setup query
    query=request.form['queryText']

    # get search results
    search_results = g.db_coll.find({'$text':{'$search':query}},
                               {'score': {'$meta': 'textScore'}})
    search_results.sort([('score', {'$meta': 'textScore'})]).limit(15)

    # collect results
    results = [result for result in search_results]

    # extract output
    results_html = ""
    for result in results:
        title = result["title"]
        asin = result["asin"]

        # get avg rating
        sum_ratings = sum([result["ratings"][key]*int(key) for key in result["ratings"]])
        count_ratings = sum([result["ratings"][key] for key in result["ratings"]])
        avg_rating = sum_ratings * 1.0 / count_ratings

        # get star image path
        rating_rounded = int(round(avg_rating * 2) * 5)
        fname = 'images/stars_{}.svg'.format(rating_rounded)
        star_path = url_for('static', filename=fname)

        #create html
        url = url_for("product", asin=asin)
        html = '<div class="search-result">'
        html += '<span class="result-title"><a href={}>{}</a></span>'.format(url, title)
        html += '<img class="stars" src="{}" />'.format(star_path)
        html += '<span class="avg-rating">{}</span></div>'.format(round(avg_rating, 2))

        results_html += html

    return render_template('search.html',
                            page_title="Search Results",
                            results=Markup(results_html)
                          )

# product
@app.route('/product/<string:asin>')
def product(asin):
    # setup vars
    product = g.db_coll.find_one({'asin':asin})
    title = product["title"]

    # get avg rating
    sum_ratings = sum([product["ratings"][key]*int(key) for key in product["ratings"]])
    count_ratings = sum([product["ratings"][key] for key in product["ratings"]])
    avg_rating = round(sum_ratings * 1.0 / count_ratings, 2)

    # get star image path
    rating_rounded = int(round(avg_rating * 2) * 5)
    fname = 'images/stars_{}.svg'.format(rating_rounded)
    star_path = url_for('static', filename=fname)

    # build html for avg_ratings
    avg_rating_html = '<img class="stars" src="{}" /><div class="avg-rating">{}</div>'.format(star_path, avg_rating)

    # build html for ratings distribution
    dist_bars_html = ""
    dist_bar_html = '<div class="bar-row"><span class="rating">{}</span>' \
            + '<span class="bar"><span class="fill" style="width:{}%;"></span></span>' \
            + '<span class="count">{}%</span></div>'

    """
    # 5 star dist
    for rating in reversed(range(1,6)):
        count = product["ratings"].get(str(rating), 0)
        bar_width = round(count * 100.0 / count_ratings, 1)
        dist_bars_html += dist_bar_html.format(rating,
                                             bar_width,
                                             bar_width)
    """

    # pos neg dist
    rating_types = {"+": (5,4), "-": (2,1)}
    for rating_type in rating_types:
        ratings = rating_types[rating_type]
        count = product["ratings"].get(str(ratings[0]), 0)
        count += product["ratings"].get(str(ratings[1]), 0)

        bar_width = round(count * 100.0 / count_ratings, 1)
        dist_bars_html += dist_bar_html.format(rating_type,
                                             bar_width,
                                             bar_width)

    # add dist bars html
    ratings_dist_html = '<div class="dist-ratings">{}</div>'.format(dist_bars_html)

    # build html for posFeatures
    feature_html = '<div class="feature-row"><div class="feature">{}</div>' \
        + '<div class="bar-row"><span class="rating"></span>' \
        + '<span class="bar"><span class="fill" style="width:{}%;"></span></span>' \
        + '<span class="value">{}%</span></div></div>'

    posFeatures_html = "None"
    if "posFeatures" in product.keys():
        posFeatures = sorted(product["posFeatures"], key=lambda x: float(x[1]))
        temp = ""
        total_importance = sum([float(feature[1]) for feature in posFeatures])
        for feature in posFeatures:
            rel_importance = round(total_importance / float(feature[1]), 1)
            temp += feature_html.format(feature[0], rel_importance, rel_importance)
        posFeatures_html = '<div class="posFeatures">{}</div>'.format(temp.strip(', '))

    # build html for negFeatures
    negFeatures_html = "None"
    if "negFeatures" in product.keys():
        negFeatures = sorted(product["negFeatures"], key=lambda x: float(x[1]))
        temp = ""
        total_importance = sum([float(feature[1]) for feature in negFeatures])
        for feature in negFeatures:
            rel_importance = round(total_importance / float(feature[1]), 1)
            temp += feature_html.format(feature[0], rel_importance, rel_importance)
        negFeatures_html = '<div class="negFeatures">{}</div>'.format(temp.strip(", "))

    return render_template(
        'product.html',
        page_title=title,
        product_title=title,
        avg_rating=Markup(avg_rating_html),
        ratings_dist=Markup(ratings_dist_html),
        pos_features=Markup(posFeatures_html),
        neg_features=Markup(negFeatures_html)
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)