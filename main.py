from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:woof@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():
    blog_id = request.args.get('id')
    
    if(blog_id):
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('main-blog.html', blog=blog)
    else:
        blogs = Blog.query.order_by(-Blog.id).all()
        return render_template('main-blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
            
        
    return render_template('new-blog.html')

if __name__ == '__main__':
    app.run()