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
	if request.method == 'POST':
		serverlog.write('\nCheck validation ')
		securitykey = request.form.get('securitykey')
		name = request.form.get('name')
		password = request.form.get('password')
		confirmpassword = request.form.get('confirmpassword')
		email = request.form.get('email')
		subject = request.form.get('select')
		classes = request.form.getlist('classes')
		print('\n\n\n\n\n\n\n\n\n\n\n\n\n',securitykey, name, password, confirmpassword, email, subject, classes)
		if True:
			serverlog.write('\nhashing')
			hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
			serverlog.write('\ngetting data')
			user = User(name=name, password=hashed_password, email =email)
			serverlog.write('\nData:'+str(user))
			db.session.add(user)
			serverlog.write('\nadded')
			serverlog.write(str(securitykey))
			db.session.commit()
			# flash(f'Your account has been created you can now login!', 'success')
			return redirect(url_for('tlogin'))

	return render_template('tregister.html', title='Teacher Register', footer=1)


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

@app.route('/home-assignment', methods = ['GET', 'POST'])
@login_required
def home_assignment():
	if not current_user.name:
		return render_template('s-home-assignment.html')
	else:
		return render_template('t-home-assignment.html')	


@app.route('/create-assignment', methods=['GET','POST'])
@login_required
def create_assignment():
	if current_user.name:
		serverlog = open('server.log','a')
		serverlog.write('\n' + str(request.method))
		if request.method == 'POST':
			serverlog.write('\nSaving File\n')
			serverlog.write(f'\n{request.form.get("testname")}\n')
			f = request.files['qpupload']
			f.save('/home/anupamkris/imgdir/QP.pdf')
			filename = request.form.get('testname')
			createfolder(filename)
			link = uploadfile('QP.pdf', filename)
			global client
			testsheet = client.open('tests')
			worksheet = testsheet.worksheet('testsheet')
			datalist = [current_user.email, request.form.get('class'), filename, link, '[]']
			worksheet.insert_row(datalist, 1)
		else:
			return render_template('create-assignment.html')
	else:
		return redirect(url_for('user_home'))
@app.route('/submit-assignment/<testname>', methods = ['GET', 'POST'])
@login_required
def submit_assignment(testname=None):
	if not current_user.name:
		if request.method == 'POST':
			serverlog = open('server.log','a')
			serverlog.write('Files : ')
			serverlog.write(str(request.files.get('assupload1')))
			serverlog.close()
			global client
			spreadsheet = client.open('tests')
			worksheet = spreadsheet.worksheet('testsheet')
			fulldata = worksheet.get_all_values()
			serverlog = open('server.log', 'a')
			serverlog.write(str(fulldata))
			print('\n\n\n\n\n\n\n\n\n\n_________________________________n\\n\n\n\n\n\n\n\n\n\n\n')
			print(fulldata)
			for i in range(len(fulldata)):
				serverlog.write(str(fulldata[i]))
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


