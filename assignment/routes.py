from flask import render_template, url_for, redirect, request
from assignment import app, db, bcrypt
from assignment.forms import RegistrationForm, LoginForm
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
	serverlog = open('server.log','a')
	if current_user.is_authenticated:
		serverlog.write('\nLogged Already')
		return redirect(url_for('home'))
	form = RegistrationForm(request.form)
	serverlog.write('\nCheck validation ')
	serverlog.write(str(form.validate_on_submit()))
	if form.validate_on_submit():
		serverlog.write('\nhashing')
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		serverlog.write('\ngetting data')
		user = User(admission=form.admission.data, password=hashed_password, email =form.email.data)
		serverlog.write('\nData:'+str(user))
		db.session.add(user)
		serverlog.write('\nadded')
		serverlog.write(str(form.dob.data))
		db.session.commit()
		# flash(f'Your account has been created you can now login!', 'success')
		return redirect(url_for('login'))
	return render_template('registerpage.html', title='Register', form=form)


@app.route('/tregister')
def tregister():
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
	return render_template('tregister.html', title='Register', form=form)
	return render_template('tregister.html')


@app.route('/login')
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm
	return render_template('login.html', form=form)

@app.route('/tlogin')
def tlogin():
	return render_template('tlogin.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/pricing')
def pricing():
	return render_template('pricing.html')

@app.route('/user-home')
def user_home():
	return render_template('user-home.html')





