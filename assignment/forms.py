from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, AnyOf
from assignment.models import User

class RegistrationForm(FlaskForm):
	admission = StringField('Admission Number', validators=[DataRequired()]
		,render_kw={'placeholder':'Admission Number'}
		)
	dob = DateField('DOB'
		,render_kw={'placeholder':'DOB'}
		)
	email = StringField('Email', validators=[DataRequired()]
		,render_kw={'placeholder':'Email'}
		)
	password = PasswordField('Password',validators=[DataRequired()]
		,render_kw={'placeholder':'Password'}
		)
	confirmpassword = PasswordField('Confirm Password'
		,validators=[DataRequired(), EqualTo('password')]
		,render_kw={'placeholder':'Confirm Password'}
		)
	submit = SubmitField('Sign Up')

	def validate_admission(self, admission):
		user = Student.query.filter_by(admission=admission.data).first()
		if user:
			raise ValidationError('The admission number entered has already registered. Try logging in')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This email is already registered. Try another email or log in.')

			 
class LoginForm(FlaskForm):
	admission = StringField('Admission Number', validators=[DataRequired()]
		,render_kw={'placeholder':'Admission Number'}
		)
	password = PasswordField('Password',validators=[DataRequired()]
		,render_kw={'placeholder':'Password'}
		)
	submit = SubmitField('Log In')


class TeacherRegistrationForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()]
		,render_kw={'placeholder':'Name'}
		)
	securitykey = StringField('Security Key'
		,validators=[DataRequired(), AnyOf(values=['qwertyuiop'])]
		,render_kw={'placeholder':'Security Key'}
		)
	email = StringField('Email', validators=[DataRequired()]
		,render_kw={'placeholder':'Email'}
		)
	password = PasswordField('Password',validators=[DataRequired()]
		,render_kw={'placeholder':'Password'}
		)
	confirmpassword = PasswordField('Confirm Password'
		,validators=[DataRequired(), EqualTo('password')]
		,render_kw={'placeholder':'Confirm Password'}
		)
	submit = SubmitField('Sign Up')


	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This email is already registered. Try another email or log in.')

class TeacherLoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired()]
		,render_kw={'placeholder':'Email'}
		)
	password = PasswordField('Password',validators=[DataRequired()]
		,render_kw={'placeholder':'Password'}
		)
	submit = SubmitField('Log In')