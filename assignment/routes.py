from flask import render_template, url_for, redirect, request
from assignment import app, db, bcrypt
from assignment.forms import RegistrationForm, LoginForm
from assignment.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html',title='Home')

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
		serverlog = open("server.log",'a')
		serverlog.write('hashing')
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		serverlog.write('getting data')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		serverlog.write('Data:',user)
		db.session.add(user)
		serverlog.write('added')
		db.session.commit()
		# flash(f'Your account has been created you can now login!', 'success')
		return redirect(url_for('login'))
	return render_template('tregister.html', title='Faculty Register', form=form)
	# return render_template('tregister.html')


@app.route('/login', methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	serverlog = open("server.log",'a')
	serverlog.write('login trial')
	serverlog.write(str(form.validate_on_submit())+'\n')
	if form.validate_on_submit():
		user = User.query.filter_by(admission=form.admission.data).first()
		serverlog.write(str(user.password))
		serverlog.write(str(form.admission.data))
		serverlog.write('is pass corect:'+str(bcrypt.check_password_hash(user.password, form.password.data)))

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('user_home'))
	return render_template('login.html', form=form, title='Student Login')

@app.route('/tlogin')
def tlogin():
	return render_template('tlogin.html', title='Faculty Login')

@app.route('/about')
def about():
	return render_template('about.html',title='About')

@app.route('/contact')
def contact():
	return render_template('contact.html',title='Contact')

@app.route('/pricing')
def pricing():
	return render_template('pricing.html',title='Pricing')

@app.route('/user-home')
@login_required
def user_home():
	return render_template('user-home.html',title='Profile', user=current_user)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


