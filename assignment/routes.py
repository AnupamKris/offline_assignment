from flask import render_template, url_for, redirect
from assignment import app, db, bcrypt
from assignment.forms import RegistrationForm
from assignment.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/register', methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		print('hashing')
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		print('getting data')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		print('Data:',user)
		db.session.add(user)
		print('added')
		db.session.commit()
		# flash(f'Your account has been created you can now login!', 'success')
		return redirect(url_for('login'))
	return render_template('registerpage.html', title='Register', form=form)

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/tregister')
def tregister():
	return render_template('tregister.html')

@app.route('/tlogin')
def tlogin():
	return render_template('tlogin.html')

