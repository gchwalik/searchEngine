# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'superfund.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    AUTHOR='author',
    TITLE='title',
    YEAR='year',
    PROJECT='project',
    KEYWORD='keyword',
    QUERY='',
    AUTHOR_QUERY='',
    TITLE_QUERY='',
    YEAR_QUERY='',
    PROJ_QUERY='',
    KEYWORD_QUERY=''
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('superfund.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/search/<choice>/<query_term>')
def search(query_term, choice):
    return _search(choice, query_term)


@app.route('/search/<choice>')
def search_empty(choice):
    return _search(choice, '')


def _search(choice, query_term):
    db = get_db()
    query = "select distinct title, author, citation, link from superfund where "+choice+" like "+"'%"+query_term+"%' order by year desc, title collate nocase asc"
    cur = db.execute(query)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)



@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        app.config['QUERY']=str(request.form['search'])
        query=app.config['QUERY']
        if query=='':
            return redirect(url_for('search_empty',choice = request.form['choice']))
        else:
            return redirect(url_for('search', query_term=query, choice = request.form['choice']))

    return render_template('login.html', error=error)


@app.route('/advanced_search',methods=['GET','POST'])
def advSearch():
  error = None
  if request.method == 'POST':
    app.config['TITLE_QUERY'] = str(request.form['title']); 
    app.config['AUTHOR_QUERY'] = str(request.form['author']); 
    app.config['YEAR_QUERY'] = str(request.form['year']);
    app.config['PROJECT_QUERY'] = str(request.form['proj_num']); 
    app.config['KEYWORD_QUERY'] = str(request.form['keyword']);     
    return redirect(url_for('AAA'))
  return render_template('adv_search.html', error=error)


@app.route('/advanced_results')
def AAA():
    db = get_db()
    query = "select distinct title, author, citation, link from superfund where author like "+"'%"+app.config['AUTHOR_QUERY']+"%'"+" and title like "+"'%"+app.config['TITLE_QUERY']+"%'"+" and year like "+"'%"+app.config['YEAR_QUERY']+"%'"+" and project_core like "+"'%"+app.config['PROJECT_QUERY']+"%'"+" and keywords like "+"'%"+app.config['KEYWORD_QUERY']+"%'"+" order by year desc, title collate nocase asc"
    cur = db.execute(query)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


if __name__ == '__main__':
    init_db()
    app.run()
