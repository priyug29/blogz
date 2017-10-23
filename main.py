from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:akshat123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner') 

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    userId = request.args.get('user')
    
    if(blog_id):
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('main-blog.html', blog=blog)
    if(userId):
        owner = User.query.filter_by(id= userId).first()
        return render_template('singleUser.html', owner=owner)
    else:
        blogs = Blog.query.order_by(-Blog.id).all()
        return render_template('main-blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        blog_title_error = ''
        if (not blog_title) or blog_title.strip() == '':
            blog_title_error = "Please fill in the title"

        blog_body_error = ''
        if (not blog_body) or blog_body.strip() == '':
            blog_body_error = "Please fill in the body"

        if blog_title_error or blog_body_error :

            return render_template('new-blog.html', blog_title_error = blog_title_error , 
                blog_body_error = blog_body_error, blog_title=blog_title, blog_body=blog_body )
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
              
    return render_template('new-blog.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']
    
    
        username_error = ''
        if (not username) or username.strip() == "" or len(username) < 3 or len(username) > 20:
            username_error = "That's not a valid username."       

        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            username_error = 'A user with that username already exists'
            return render_template('/signup.html', username_error=username_error, username=username)

        password_error = ''    
        if (not password) or password.strip() == "" or len(password) < 3 or len(password) > 20:
            password_error = "That's not a valid password."


        verify_password_error = ''
        if verify_password != password or verify_password == '':
            verify_password_error = "Password don't match."
            verify_password = ''

    
        if username_error or password_error or verify_password_error :
            return render_template('signup.html', username_error=username_error, password_error=password_error, 
                verify_password_error=verify_password_error, username=username)
        

       

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['username'] = user.username
                #flash('welcome back, '+user.username)
                return redirect("/newpost")
            else :
                error = "Invalid Password"
        else :
            error = "Invalid Username"
            
        if(error):
            return render_template('login.html', error=error)        
        #flash('bad username or password')
        return redirect("/login")

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/")
def index():
    encoded_error = request.args.get("error")
    users = User.query.all()
    return render_template('index.html', users=users, 
        error=encoded_error and cgi.escape(encoded_error, quote=True))

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    print(request.endpoint)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    

if __name__ == '__main__':
    app.run()