from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from assignment.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired(),Length(min=3, max=20)])
	password = PasswordField('Password',validators=[DataRequired()])
	confirmpassword = PasswordField('Confirm Password',
		validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')