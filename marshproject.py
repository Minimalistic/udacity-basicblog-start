import os
import webapp2
import re

import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

"""ADD DOCUMENTATION describing StevesBlogHandler """

class StevesBlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

def render_post(response, post):
	response.out.write('<br>' + post.subject + '</b><br>')
	response.out.write(post.content)

""" Form submission processing functions provided by Udacity """

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Base(StevesBlogHandler):
	def get(self):
		self.render("base.html")

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class BlogFront(StevesBlogHandler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render('blog.html', posts = posts)

class PostPage(StevesBlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class SignUp(StevesBlogHandler):

	def get(self):
		self.render("signup.html")

	def post(self):
		have_error = False
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')

		params = dict(username = username,
						email = email)

		if not valid_username(username):
			params['error_username'] = "That's not a valid username."
			have_error = True

		if not valid_password(password):
			params['error_password'] = "That isn't a valid password."
			have_error = True
		elif password != verify:
			params['error_verify'] = "Passwords entered were not identical."
			have_error = True

		if not valid_email(email):
			params['error_email'] = "That's not a valid email."
			have_error = True

		if have_error:
			self.render('signup.html', **params)
		else:
			self.redirect('/blog/welcome?username=' + username)

class Welcome(StevesBlogHandler):
	def get(self):
		username = self.request.get('username')
		if valid_username(username):
			self.render('welcome.html', username = username)
		else:
			self.redirect('/signup')

class Login(StevesBlogHandler):
	def get(self):
		self.render("login.html")

class Logout(StevesBlogHandler):
	def get(self):
		self.render("logout.html")

class NewPost(StevesBlogHandler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')

		if subject and content:
			p = Post(parent = blog_key(), subject = subject, content = content)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))
		else:
			error = "subject and content, please!"
			self.render("newpost.html", subject=subject, content=content, error=error)

app = webapp2.WSGIApplication([('/', Base),
								('/blog/?', BlogFront),
								('/signup', SignUp),

								('/login', Login),
								('/logout', Logout),

								('/blog/([0-9]+)', PostPage),
								('/blog/newpost', NewPost),

								('/blog/welcome', Welcome),
								], debug=True)