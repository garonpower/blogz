from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:R2ykpwie0McOfayP@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    posted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.posted = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def user_input_verification(user_input):
    if len(user_input) > 0:
        for space in user_input:
            if space == ' ':
                return False

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("You have successfully logged in!", 'notice')
            return redirect ('/newpost')
        if user and user.password != password:
            flash('Invalid password', 'error')
        else:
            flash('Username does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists', 'error')

        if (not username) or (username.strip() == ""):
            flash('Please input a Username (greater than 3 characters)', 'error')
        
        if (not password) or (password.strip() == ""):
            flash('Please input a password (greater than 3 characters)', 'error')
        
        if (not verify) or (verify.strip() == ""):
            flash('Please input a matching password', 'error')

        if user_input_verification(username) == False:
            flash('Spaces are not allowed!', 'error')
            return render_template('signup.html')

        if user_input_verification(password) == False:
            flash('Spaces are not allowed!', 'error')
            return render_template('signup.html')
       
        if password != verify:
            flash("Passwords don't match (must be longer than 3 characters)", 'error')
        
        if len(username) and len(password) < 3:
            flash('Username and password must be greater than 3 characters', 'error')

        else:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

    return render_template('signup.html')

# @app.route('/index', methods=['POST', 'GET'])

@app.route('/logout')
def logout():   
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog(): 

    posts = Blog.query.filter_by(posted=False).all()
    posted_blogs = Blog.query.filter_by(posted=True).all()

    return render_template('blog.html', title = 'Build A Blog',
    posts=posts, posted_blogs=posted_blogs)

@app.route('/completed_posts', methods=['POST'])
def completed_posts():

    title_id = int(request.form['title-id'])
    title_post = Blog.query.get(title_id)
    content_id = int(request.form['content-id'])
    content_post = Blog.query.get(content_id)
    title_post.completed = True
    content_post.completed = True
    db.session.add(title_post)
    db.session.add(content_post)
    db.session.commit()

    return redirect('/blog')

@app.route('/newpost')
def display_blog_entry():
    return render_template('newpost.html',title="Add Blog Entry")

@app.route('/newpost', methods=['POST', 'GET'])
def add_blog_entry():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']

        title_error = ''
        content_error = ''

        if (not post_title) or (post_title.strip() == ""):
            title_error = "Please fill in the title"

        if (not post_content) or (post_content.strip() == ""):
            content_error = "Please fill in the body"
        
        if not title_error and not content_error:
            new_post = Blog(post_title,post_content)
            db.session.add(new_post)
            db.session.commit()
            blog = new_post.id
            return redirect('/blog_post?id=' + str(blog))
        else:
            return render_template('/newpost.html', 
                title_error=title_error,
                content_error=content_error, 
                post_title=post_title,
                post_content=post_content)


@app.route('/blog_post', methods=['POST', 'GET'])
def blog_post():
    if request.method == 'GET':
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)

        return render_template('blog_post.html',  blog=blog)


if __name__ == '__main__':
    app.run()