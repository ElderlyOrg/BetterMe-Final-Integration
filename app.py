from flask import Flask, render_template, request, redirect, url_for, session, flash  # For flask implementation
from bson import ObjectId  # For ObjectId to work
from pymongo import MongoClient
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')
title = "TODO"
heading = "TODO"

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
db = client.mymongodb  # Select the database
todos = db.todo  # Select the collection name
notes = db.note


def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')


@app.route("/list")
def lists():
    # Display the all Tasks
    useri = session.get('user')
    if useri:
        todos_l = todos.find({"user.email": useri['email']})
        notes_l = notes.find({"user.email": useri['email']})
    else:
        todos_l = todos.find()
        notes_l = notes.find()
    a1 = "active"
    return render_template('index.html', a1=a1, todos=todos_l, t=title, h=heading, user=useri, notes=notes_l)


@app.route("/listn")
def listsn():
    # Display the all notes
    useri = session.get('user')
    if useri:
        todos_l = todos.find({"user.email": useri['email']})
        notes_l = notes.find({"user.email": useri['email']})
    else:
        todos_l = todos.find()
        notes_l = notes.find()
    a1 = "active"
    return render_template('index.html', a1=a1, t=title, todos=todos_l, h=heading, user=useri, notes=notes_l)


@app.route("/completed")
def completed():
    # Display the Completed Tasks
    useri = session.get('user')
    todos_l = todos.find({"done": "yes"})
    a3 = "active"
    return render_template('index.html', a3=a3, todos=todos_l, t=title, h=heading, user=useri)


@app.route("/done")
def done():
    # Done-or-not ICON
    id = request.values.get("_id")
    task = todos.find({"_id": ObjectId(id)})
    if task[0]["done"] == "yes":
        todos.update({"_id": ObjectId(id)}, {"$set": {"done": "no"}})
    else:
        todos.update({"_id": ObjectId(id)}, {"$set": {"done": "yes"}})
    redir = redirect_url()

    return redirect(redir)


@app.route("/action", methods=['POST'])
def action():
    # Adding a Task
    name = request.values.get("name")
    desc = request.values.get("desc")
    date = request.values.get("date")
    pr = request.values.get("pr")
    user = session.get('user')
    todos.insert({"name": name, "desc": desc, "date": date, "pr": pr, "done": "no", "user": user})
    return redirect("/list")


@app.route("/notestore", methods=['POST'])
def note():
    # Adding a Notes
    note = request.values.get("note")
    user = session.get('user')
    notes.insert({"note": note, "user": user})
    return redirect("/listn")


@app.route("/remove")
def remove():
    # Deleting a Task with various references
    key = request.values.get("_id")
    todos.remove({"_id": ObjectId(key)})
    return redirect("/")


@app.route("/removen")
def removen():
    # Deleting a task with various references
    key = request.values.get("_id")
    notes.remove({"_id": ObjectId(key)})
    return redirect("/")


@app.route("/update")
def update():
    id = request.values.get("_id")
    useri = session.get('user')
    task = todos.find({"_id": ObjectId(id)})
    return render_template('update.html', tasks=task, h=heading, t=title, user=useri)


@app.route("/action3", methods=['POST'])
def action3():
    # Updating a Task with various references
    name = request.values.get("name")
    desc = request.values.get("desc")
    date = request.values.get("date")
    pr = request.values.get("pr")
    id = request.values.get("_id")
    todos.update({"_id": ObjectId(id)}, {'$set': {"name": name, "desc": desc, "date": date, "pr": pr}})
    return redirect("/")


@app.route("/search", methods=['GET'])
def search():
    # Searching a Task with various references
    useri = session.get('user')
    key = request.values.get("key")
    refer = request.values.get("refer")
    if key == "_id":
        todos_l = todos.find({refer: ObjectId(key)})
    else:
        todos_l = todos.find({refer: key})
    return render_template('searchlist.html', todos=todos_l, t=title, h=heading, user=useri)


@app.route('/')
def homepage():
    useri = session.get('user')
    if useri:
        todos_l = todos.find({"user.email": useri['email']})
        notes_l = notes.find({"user.email": useri['email']})
    else:
        todos_l = todos.find()
        notes_l = notes.find()
    a2 = "active"
    return render_template('index.html', a2=a2, todos=todos_l, t=title, h=heading, user=useri, notes=notes_l)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['user'] = user
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('bye.html')
