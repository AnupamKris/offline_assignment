from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from assignment.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired(),Length(min=3, max=20)]
		,render_kw={"placeholder": "Username"}
		)
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