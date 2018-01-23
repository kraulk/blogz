from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

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

	def __init__(self, title, content):
		self.title = title
		self.content = content

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(120))
	# TODO use pw hash for security reasons
	password = db.Colum(db.String(999))
	blogs = db.relationship('Blog', backref = 'id')

	def __init__(self, username, password):
		self.username = username
		self.password = password


def is_empty(text):
	if len(text) == 0:
		return True

@app.route('/blog')
def blog():

	post_id = request.args.get('id')

	if (post_id):
		post = Blog.query.get(post_id)
		return render_template('post.html', title='new post', post=post)

	all_posts = Blog.query.order_by(Blog.id.desc()).all()
	return render_template('blog.html', all_posts=all_posts)


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

	if request.method == 'POST':
		title = request.form['title']
		content = request.form['content']
		new_post = Blog(title, content)

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

if __name__ == '__main__':
	app.run()
