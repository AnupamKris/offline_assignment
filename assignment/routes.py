from flask import render_template, url_for, redirect, request
from assignment import app, db, bcrypt
from assignment.forms import RegistrationForm, LoginForm, TeacherRegistrationForm, TeacherLoginForm
from assignment.models import User
from flask_login import login_user, current_user, logout_user, login_required
from random import choice
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from mediafire.client import MediaFireClient, File, Folder

scope = ['https://www.googleapis.com/auth/drive']

cred = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)

client = gspread.authorize(cred)

def createfolder(foldername):
    client = MediaFireClient()
    client.login( email='mediamngeforkvhvf@gmail.com',
        password='hard2reach',
        app_id='42511')
    client.create_folder('/'+foldername)

def uploadfile(filename, foldername):
    imagepath = '/home/mngeforkvhvf/savedir/'
    imagepath+=filename
    print(imagepath)
    print(filename)
    client = MediaFireClient()
    print('login')
    client.login( email='mediamngeforkvhvf@gmail.com',
        password='hard2reach',
        app_id='42511')
    for i in range(20):
        try:
            print('doing upload')
            result = client.upload_file(imagepath, "mf:/{foldername}/")
            fileinfo = client.api.file_get_info(result.quickkey)
            link = fileinfo['file_info']['links']['normal_download']
            break   
        except:
            print('retrying')
    
    return link

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

	return render_template('registerpage.html', title='Register', form=form, footer=1)

@app.route('/tregister', methods = ['GET','POST'])
def tregister():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	serverlog = open('server.log','a')
	if current_user.is_authenticated:
		serverlog.write('\nLogged Already')
		return redirect(url_for('home'))
	form = TeacherRegistrationForm(request.form)
	serverlog.write('\nCheck validation ')
	serverlog.write(str(form.validate_on_submit()))
	if form.validate_on_submit():
		serverlog.write('\nhashing')
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		serverlog.write('\ngetting data')
		user = User(name=form.name.data, password=hashed_password, email =form.email.data)
		serverlog.write('\nData:'+str(user))
		db.session.add(user)
		serverlog.write('\nadded')
		serverlog.write(str(form.securitykey.data))
		db.session.commit()
		# flash(f'Your account has been created you can now login!', 'success')
		return redirect(url_for('tlogin'))

	return render_template('tregister.html', title='Teacher Register', form=form, footer=1)


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
	return render_template('login.html', form=form, title='Student Login', footer=1)

@app.route('/tlogin', methods = ['GET', 'POST'])
def tlogin():
	global current_user
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = TeacherLoginForm()
	serverlog = open("server.log",'a')
	serverlog.write('login trial')
	serverlog.write(str(form.validate_on_submit())+'\n')
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		serverlog.write(str(user.password))
		serverlog.write(str(form.email.data))
		serverlog.write('is pass corect:'+str(bcrypt.check_password_hash(user.password, form.password.data)))

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			serverlog.write('LOGGING TEACHER:'+user.email+user.name+current_user.email+current_user.name)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('user_home'))
	return render_template('tlogin.html', form=form, title='Faculty Login', footer=1)

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
	global current_user
	if not current_user.name:
		student = client.open('classdetails').sheet1
		s_adm = student.col_values(1)
		fields = student.row_values(1)
		current_student = {}
		file = open('server.log','a')
		file.write('\nTeacher ::::: ' + str(current_user.admission))
		file.write('\n' + str(current_user.name))
		file.close()
		for i in s_adm:
			if i == current_user.admission:
				row = student.row_values(s_adm.index(i)+1)
		for i in range(13):
			current_student[fields[i]] = row[i]
		return render_template('user-home.html',title='Profile', user=current_user, choice = choice, student=current_student)
	else:
		current_teacher = {'Name':current_user.name, 'Class':1, 'Section':5}
		return render_template('t-user-home.html',title='Profile', user=current_user, choice = choice, teacher=current_teacher)

@app.route('/home-assignment')
@login_required
def home_assignment():
	return render_template('t-home-assignment.html', choice=choice)	

@app.route('/create-assignment', methods=['GET','POST'])
@login_required
def create_assignment():
	return render_template('create-assignment.html')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


