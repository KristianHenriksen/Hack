from flask import render_template, flash, redirect, url_for, request, session
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

#Generate password hash
app.secret_key = 'SECRET_KEY'

#add max length for file uploads in bytes
app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1000

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    session.clear()
    if form.login.is_submitted() and form.login.submit.data:
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data.replace('"', '""')),(form.login.username.data))
        if user == None:
            flash('Sorry, this user does not exist!')
        elif check_password_hash(user['password'], form.login.password.data):
            session['username'] = form.login.username.data
            return redirect(url_for('stream'))
        else:
            flash('Sorry, wrong password!')

    elif form.register.is_submitted() and form.register.submit.data:

        #check if username is taken
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.register.username.data), one=True)
        
        if user != None:
            flash('Sorry, username is already taken!')
            return render_template('index.html', title='Welcome', form=form)

        #check for valid password for new users
        if form.register.password.data and form.register.password.data == form.register.confirm_password.data:
            query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
            form.register.last_name.data, generate_password_hash(form.register.password.data)))
            return redirect(url_for('index'))
        else: flash('Sorry, not valid password!')

    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream', methods=['GET', 'POST'])
def stream():
    form = PostForm()
    username=session.get('username', None)
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        if form.image.data:
            if form.image.data.content_type != "image/png":
                return
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)


        query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data.replace('"', '""'), form.image.data.filename, datetime.now()))

        return redirect(url_for('stream'))

    posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<int:p_id>', methods=['GET', 'POST'])
def comments(p_id):
    form = CommentsForm()
    username=session.get('username', None)
    if form.is_submitted():
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends', methods=['GET', 'POST'])
def friends():
    form = FriendsForm()
    username=session.get('username', None)
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data.replace('"', '""')),(form.login.username.data))
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username=session.get('username', None)
    form = ProfileForm()
    if form.is_submitted():
        query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        ))
        return redirect(url_for('profile', username=username))
    
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return render_template('profile.html', title='profile', user=user, form=form)