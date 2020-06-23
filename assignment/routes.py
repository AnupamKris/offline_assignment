from flask import render_template, url_for, redirect, request
from assignment import app, db, bcrypt
from assignment.forms import RegistrationForm, LoginForm, TeacherRegistrationForm, TeacherLoginForm
from assignment.models import User, Teacher
from flask_login import login_user, current_user, logout_user, login_required
from random import choice
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from mediafire.client import MediaFireClient, File, Folder
import pandas as pd

scope = ['https://www.googleapis.com/auth/drive']

cred = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)

client = gspread.authorize(cred)

current_teacher = {}

def createfolder(foldername):
    client = MediaFireClient()
    client.login( email='mngeforkvhvf@gmail.com',
        password='hard2reach',
        app_id='42511')
    client.create_folder('/'+foldername)

def uploadfile(filename, foldername):
    imagepath = '/home/anupamkris/imgdir/'
    imagepath+=filename
    print(imagepath)
    print(filename)
    client = MediaFireClient()
    print('login')
    client.login( email='mngeforkvhvf@gmail.com',
        password='hard2reach',
        app_id='42511')
    for i in range(20):
    	# try:
        	print('doing upload')
        	result = client.upload_file(imagepath, f"mf:/{foldername}/")
        	fileinfo = client.api.file_get_info(result.quickkey)
        	link = fileinfo['file_info']['links']['normal_download']
        	break   
    	# except:
        	print('retrying')    
    return link

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html',title='Home')

fullstudentdata = pd.read_excel('/home/anupamkris/Desktop/offline_assignment/offline_assignment/assignment/static/students.xlsx')

@app.route('/register', methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	if current_user.is_authenticated:
	
		return redirect(url_for('home'))
	form = RegistrationForm(request.form)


	if form.validate_on_submit():
	
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
	
		user = User(admission=form.admission.data, password=hashed_password, email =form.email.data)
	
		db.session.add(user)
	
	
		db.session.commit()
		# flash(f'Your account has been created you can now login!', 'success')
		return redirect(url_for('login'))

	return render_template('registerpage.html', title='Register', form=form, footer=1)

@app.route('/tregister', methods = ['GET','POST'])
def tregister():
	if current_user.is_authenticated:
		return redirect(url_for('home'))


	if current_user.is_authenticated:
	
		return redirect(url_for('home'))
	if request.method == 'POST':
	
		securitykey = request.form.get('securitykey')
		name = request.form.get('name')
		password = request.form.get('password')
		confirmpassword = request.form.get('confirmpassword')
		email = request.form.get('email')
		subject = request.form.get('select')
		classes = request.form.getlist('classes')
		classteacherof = request.form.get('classteacherof')
		global client
		spreadsheet = client.open('teachers')
		worksheet = spreadsheet.worksheet('Sheet1')
		teacherdetails = [str(name), str(email), str(subject), str(classes), str(classteacherof)]
		worksheet.insert_row(teacherdetails,2)
		print('\n\n\n\n\n\n\n\n\n\n\n\n\n',securitykey, name, password, confirmpassword, email, subject, classes)
		if True:
		
			hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
		
			user = User(name=name, password=hashed_password, email =email)
		
			db.session.add(user)
		
		
			db.session.commit()
			teacher = Teacher(name=name, email=email, classeshandled =str(classes), classteacher=classteacherof, subject=subject)
			db.session.add(teacher)
			db.session.commit()
			# flash(f'Your account has been created you can now login!', 'success')
			return redirect(url_for('tlogin'))

	return render_template('tregister.html', title='Teacher Register', footer=1)


@app.route('/login', methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()



	if form.validate_on_submit():
		user = User.query.filter_by(admission=form.admission.data).first()
	
	
	

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



	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
	
	
	

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
		
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
		s_adm = fullstudentdata['admission']
		fields = list(fullstudentdata.columns)
		current_student = {}
		row = list(fullstudentdata.loc[fullstudentdata['admission'] == int(current_user.admission)].values[0])
		for i in range(5):
			current_student[fields[i]] = row[i]

		print('\n\n Stud Data', current_student)

		return render_template('user-home.html',title='Profile', user=current_user, choice = choice, student=current_student)
	else:
		global current_teacher
		spreadsheet = client.open('teachers')
		worksheet = spreadsheet.worksheet('Sheet1')
		t_email = worksheet.col_values(2)
		fields = worksheet.row_values(1)
		current_teacher = {}
		for i in t_email:
			if i == current_user.email:
				row = worksheet.row_values(t_email.index(i)+1)
		for i in range(6):
			current_teacher[fields[i]] = row[i]
		print(current_teacher)
		return render_template('t-user-home.html',title='Profile', user=current_user, choice = choice, teacher=current_teacher, eval=eval, len=len)

@app.route('/home-assignment', methods = ['GET', 'POST'])
@login_required
def home_assignment():
	if not current_user.name:
		return render_template('s-home-assignment.html')
	else:
		tests = client.open('tests')
		testsheet = tests.worksheet('testsheet')
		emails = testsheet.col_values(1)
		teacher_tests = []
		for i in emails:
			if i == current_user.email:
				row = testsheet.row_values(emails.index(i)+1)
				teacher_tests.append(row)
		if teacher_tests:
			print('\n\n\n\n\n'+teacher_tests+'\n\n\n\n\n\n')
		else:
			print('\n\n\n\n\n\n\n\nNo tests yet\n\n\n\n\n\n')
		return render_template('t-home-assignment.html', teacher = current_teacher)	


@app.route('/create-assignment', methods=['GET','POST'])
@login_required
def create_assignment():
	if current_user.name:
	
	
		if request.method == 'POST':
		
		
			f = request.files['qpupload']
			f.save('/home/anupamkris/imgdir/QP.pdf')
			filename = request.form.get('testname')
			createfolder(filename)
			link = uploadfile('QP.pdf', filename)
			global client
			testsheet = client.open('tests')
			worksheet = testsheet.worksheet('testsheet')
			datalist = [current_user.email, request.form.get('class'), filename, link, '[]']
			worksheet.insert_row(datalist, 2)
		else:
			return render_template('create-assignment.html', teacher = current_teacher, eval = eval)
	else:
		return redirect(url_for('user_home'))
@app.route('/submit-assignment/<testname>', methods = ['GET', 'POST'])
@login_required
def submit_assignment(testname=None):
	if not current_user.name:
		if request.method == 'POST':
		
		
		
		
			global client
			spreadsheet = client.open('tests')
			worksheet = spreadsheet.worksheet('testsheet')
			fulldata = worksheet.get_all_values()
		
		
			print('\n\n\n\n\n\n\n\n\n\n_________________________________n\\n\n\n\n\n\n\n\n\n\n\n')
			print(fulldata)
			for i in range(len(fulldata)):
			
				if fulldata[i][2] == testname:
					print(fulldata[i][2])
					dd = {}
					exec(f"updata = {fulldata[i][4]}", dd)	
					updata = dd['updata']
					print('\n\n\n\n\n\n\n', updata)
					try:
						print('running Try block')
						if len(updata) == 0:
							raise Error
						for j in updata:
							print(j)
							if current_user.admission in list(j.values()):
								print('running if')
								print('\n\n\n\n\n\n\n\n Already Submitted you fool! \n\n\n\n\n\n\n\n')
								return render_template('register.html')
						else:
							f = request.files['assupload']
							f.save('/home/anupamkris/imgdir/'+current_user.admission+'.pdf')
							link = uploadfile(current_user.admission+'.pdf', testname)
							print('running else')
							updata.append({'admno':current_user.admission, 'link':link, 'marks':None})
							worksheet.update_cell(i+1, 5, str(updata))
					except:
						f = request.files['assupload']
						f.save('/home/anupamkris/imgdir/'+current_user.admission+'.pdf')
						link = uploadfile(current_user.admission+'.pdf', testname)
						print('running except')
						updata.append({'admno':current_user.admission, 'link':link, 'marks':None})
						print(updata)
						worksheet.update_cell(i+1, 5, str(updata))
			return render_template('successpage')
		else:
			return render_template('submit-assignment.html')


@app.route('/sample-pdf-viewer')
@login_required
def pdf_viewer():
	return render_template('embedpdf.html')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


