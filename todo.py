# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify
from tsql import *
import json

# configuration
DEBUG = True
SECRET_KEY = 'development key'

# create out little application
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def home_page():
    return render_template('Todos.html')


@app.route('/fetch_todos/<id>', methods=['DELETE', 'PUT'])
def fetch_todos_del(id):
    qsession = get_session()
    cur_todo = qsession.query(todos).get(id)
    if request.method == 'DELETE':
        qsession.delete(cur_todo)
        qsession.commit()
    elif request.method == 'PUT':
        cur_todo.done = request.json.get('done')
        cur_todo.todotext = request.json.get('title')
        qsession.commit()
        res = cur_todo.to_dict()
        return jsonify(res)

    return json.dumps('clear ok')


def add_model_db(title, userid):
    qsession = get_session()
    newtodo = todos(
        todotext=title,
        userid=userid
    )
    qsession.add(newtodo)
    qsession.commit()
    return newtodo


@app.route('/fetch_todos', methods=['GET', 'POST'])
def fetch_todos():
    if request.method == 'POST':
        title = request.json.get('title')
        userid = session['cur_user_id']
        newtodo = add_model_db(title, userid)
        res = newtodo.to_dict()
        return jsonify(res)

    elif request.method == 'GET':
        qsession = get_session()
        todo_items = qsession.query(todos).filter_by(userid=session['cur_user_id']).all()
        todo_dict_list = []
        for todo_item in todo_items:
            todo_item = todo_item.to_dict()
            todo_dict_list.append(todo_item)
        res = {'data': todo_dict_list}
        return jsonify(res)


def add_user(username, userpasswd):
    admin = usertable(
        name=username,
        passwd=userpasswd)

    qsession = get_session()
    qsession.add(admin)
    qsession.commit()


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        userpasswd = request.form['password']
        add_user(username, userpasswd)
        flash('you were register')
        return redirect(url_for('home_page'))

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        qsession = get_session()
        username = request.form['username']
        query = qsession.query(usertable).filter_by(name=username).first()
        if (query != None):
            if request.form['username'] != query.name:
                error = 'Invalid username'
            elif request.form['password'] != query.passwd:
                print query.passwd
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                session['cur_username'] = request.form['username']
                session['cur_user_id'] = query.userid
                flash('you were logged in')

                return redirect(url_for('home_page'))
        else:
            error = 'no username, please register'

    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    session['cur_user_id'] = None
    flash('you were logged out')
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run()
