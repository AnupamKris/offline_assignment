from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin 

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	admission = db.Column(db.String(20), unique=True, nullable=True)
	password = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(120), nullable=False)
	name = db.Column(db.String(120), nullable=True)

	
	def __repr__(self):
		return f"User('{self.admission}','{self.password}','{self.email}')"

class Teacher(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(25), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	classeshandled = db.Column(db.String(120), nullable=False)
	classteacher = db.Column(db.String(120), nullable=False)
	subject = db.Column(db.String(120), nullable=False)
	

	def __repr__(self):
		return f"Teacher('{self.name}','{self.email}','{self.classteacher}','{self.classeshandled}','{self.subject}')"