from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'mysecretkeyis'

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(120))
	content = db.Column(db.Text)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, title, content, owner):
		self.title = title
		self.content = content
		self.owner = owner

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(120))
	# TODO use pw hash for security
	password = db.Column(db.String(999))
	blogs = db.relationship('Blog', backref = 'owner')

	def __init__(self, username, password):
		self.username = username
		self.password = password


def is_empty(text):
	if len(text) == 0:
		return True

def has_space(input):
	if ' ' in input:
		return True

def within_character_limit(input):
	if 2 < len(input) < 21:
		return True

def passwords_match(password, verification):
	if password == verification:
		return True


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog')
def blog():

	post_id = request.args.get('id')

	if post_id:
		post = Blog.query.get(post_id)
		return render_template('post.html', title='Post', post=post)

	user_id = request.args.get('user')
	if user_id:
		user_posts = Blog.query.filter_by(owner_id=user_id).all()
		user_display = User.query.filter_by(id=user_id).first()
		return render_template('user-posts.html', tite='User Posts',
								user_posts=user_posts,
								user_display=user_display)

	all_posts = Blog.query.order_by(Blog.id.desc()).all()
	return render_template('blog.html', all_posts=all_posts)


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

	if request.method == 'POST':
		title = request.form['title']
		content = request.form['content']
		owner = User.query.filter_by(username=session['username']).first()
		new_post = Blog(title, content, owner)


		if is_empty(title) or is_empty(content):
			flash('You must have a title and content to post a new blog.', 'error')
			return render_template('new-post.html', title=title, content=content)
		
		else:
			db.session.add(new_post)
			db.session.commit()
			url = "/blog?id=" + str(new_post.id)
			return redirect(url)

	else:
		return render_template('new-post.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()

		if user and user.password == password:
			session['username'] = username
			return redirect('/new-post')
	
		# User does not exist
		elif not user:
			flash('Username does not exist', 'error')
			return redirect('/login')

		# User exists, but password is wrong
		elif user.password != password:
			flash('Password is incorrect.', 'error')
			return redirect('/login')



	return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		verify = request.form['verify']

		error_username = ''
		error_password = ''
		error_verify = ''

		existing_user = User.query.filter_by(username=username).first()
		
		if (	is_empty(username)
			or 	is_empty(password)
			or 	is_empty(verify)
			):
			flash('One or more fields is invalid', 'error')
			return render_template('signup.html', username=username)

		if existing_user:
			flash('Username already exists', 'error')
			return redirect('/signup')

		if not existing_user:

			# Username validation
			# Errors if blank, outside character limit, or has space
			if (     is_empty(username)
				or   has_space(username)
				or   not within_character_limit(username)
				):
				error_username = "That's not a valid username"

			# Password validation
			# Errors if blank, oustisde character limit, or has space 
			if (     is_empty(password)
				or   has_space(password)
				or   not within_character_limit(password)
				):
				error_password = "That's not a valid password"

			# Password verification validation
			# Errors if blank, does not match password
			if (     is_empty(verify)
				or   not passwords_match(password,verify)
				):
				error_verify = "Passwords don't match"	

			if (    not error_username
				and not error_password
				and not error_verify
				):
				new_user = User(username, password)
				db.session.add(new_user)
				db.session.commit()
				session['username'] = username
				return redirect('/new-post')

			return render_template('signup.html', 
							username=username,
							error_username=error_username,
							error_password=error_password,
							error_verify=error_verify,
							title='Signup')

	return render_template('signup.html')

@app.route('/logout')
def logout():
	del session['username']
	return redirect('/blog')

@app.route('/')
def index():
	title = 'Index'
	all_users = User.query.order_by(User.username.asc()).all()
	return render_template('index.html', title=title, all_users=all_users)


if __name__ == '__main__':
	app.run()
