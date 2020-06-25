from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
# from flask_mail import Mail
import json
import os
import math
from datetime import datetime


with open('config.json', 'r') as c:
    params = json.load(c)['params']

local_server = True
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME = params['gmail-user'],
#     MAIL_PASSWORD=  params['gmail-password']
# )
# mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)

class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)     



@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    #[0: params['no_of_posts']]
    #posts = posts[]
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page= int(page)
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    #Pagination Logic
    #First
    if (page==1):
        prev = "#"
        next = "/?page="+ str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    if ('user' in session):
    	var = "logout"
    	url="logout"
    
    else:
    	var="login"
    	url="dashboard"



    return render_template('index.html', params=params, posts=posts, prev=prev, next=next,var=var,url=url)



@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    if ('user' in session):
    	var = "logout"
    	url="logout"
    else:
    	var="login"
    	url="dashboard"
    return render_template('post.html', params=params, post=post,var=var,url=url)

@app.route("/about")
def about():
	if ('user' in session):
		var = "logout"
		url="logout"
	else:
		var="login"
		url="dashboard"
	return render_template('about.html', params=params,var=var,url=url)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
	if request.method=='POST':
		semail = request.form.get('semail')
		sname = request.form.get('sname')
		spass = request.form.get('spass')
		users = Users(email=semail, name=sname, password=spass)
		db.session.add(users)
		db.session.commit()
		session['user'] = sname
		posts = Posts.query.all()
		return render_template('dashboard.html', params=params, posts = posts, sname=sname)
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
	if request.method=='POST':
		useremail = request.form.get('uemail')
		userpass = request.form.get('pass')
		db=Users.query.filter_by(email=useremail).first()
		dbpass=db.password
		dbuseremail=db.email
		if (useremail == dbuseremail and userpass == dbpass):
			#set the session variable
			username=db.name
			session['user'] = username
			posts = Posts.query.all()
			var = "logout"
			url="logout"
			return render_template('dashboard.html', params=params, posts = posts, sname=username,var=var,url=url)
		else:
			return "wrong"
	if ('user' in session):
		posts = Posts.query.all()
		username=session['user']
		var = "logout"
		url="logout"
		return render_template('dashboard.html', params=params, posts = posts,sname=username,var=var,url=url)		

	return render_template('loginnew.html', params=params)    

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno=='0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        var = "logout"
        url="logout"
        return render_template('edit.html', params=params, post=post, sno=sno,var=var,url=url)


@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        var = "logout"
        url="logout"
    return redirect('/dashboard',var=var,url=url)

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session):
        if (request.method == 'POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return "Uploaded successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/')



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New message from ' + name,
        #                   sender=email,
        #                   recipients = [params['gmail-user']],
        #                   body = message + "\n" + phone
        #                   )
    if ('user' in session):
        var = "logout"
        url="logout"
    else:
        var="login"
        url="dashboard"
    return render_template('contact.html', params=params,var=var,url=url)


app.run(debug=True)


