from flask import render_template, flash, url_for, redirect, request, session
from assignment import app, db, bcrypt
from assignment.forms import RegistrationForm, LoginForm, TeacherRegistrationForm, TeacherLoginForm
from assignment.models import User, Teacher
from flask_login import login_user, current_user, logout_user, login_required
from random import choice
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from mediafire.client import MediaFireClient, File, Folder
import pandas as pd
import os
from PIL import Image
import img2pdf
# GSpread---------------------------------------------------------------------------
scope = ['https://www.googleapis.com/auth/drive']

cred = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/anupamkris/mnge/offline_assignment/assignment/cred.json', scope)
# cred = ServiceAccountCredentials.from_json_keyfile_name(
#  "/home/anupamkris/mnge/offline_assignment/cred.json", scope)


client = gspread.authorize(cred)
# ----------------------------------------------------------------------------------

# Student Excel Loading-------------------------------------------------------------
fullstudentdata = pd.read_excel(
    "/home/anupamkris/mnge/offline_assignment/assignment/static/students.xlsx")
# fullstudentdata = pd.read_excel(
#    "/home/anupamkris/mnge/offline_assignment/assignment/static/students.xlsx")
# Bye
s_adm = fullstudentdata['admission']

fields = list(fullstudentdata.columns)
# ----------------------------------------------------------------------------------


def createfolder(foldername):
    client = MediaFireClient()
    client.login(email='media.mngeforhvf@gmail.com',
                 password='hard2reach',
                 app_id='42511')
    client.create_folder('/'+foldername)


def uploadfile(filename, foldername):
    imagepath = ''
    imagepath += filename
    print(imagepath)
    print(filename)
    client = MediaFireClient()
    print('login')
    client.login(email='media.mngeforhvf@gmail.com',
                 password='hard2reach',
                 app_id='42511')
    for i in range(20):
        try:
            print('doing upload')
            result = client.upload_file(imagepath, f"mf:/{foldername}/")
            fileinfo = client.api.file_get_info(result.quickkey)
            link = fileinfo['file_info']['links']['normal_download']
            break
        except:
            print('retrying')
    return link


@app.route('/')
@app.route('/home')
def home():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            # os.remove(
            # 	f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    return render_template('home.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            # os.remove(
            # f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm(request.form)

    global fullstudentdata

    if form.validate_on_submit():

        cur_student = fullstudentdata.loc[fullstudentdata['admission'] == int(
            form.admission.data)]
        print('\n\n\n\n\n\n\n\n\n', cur_student, '\n\n\n\n\n\n', form.dob.data)
        rawdob = str(form.dob.data).split('-')[::-1]
        dob = '/'.join(rawdob)
        print(dob)
        if cur_student['dob'].values == dob:

            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')

            user = User(admission=form.admission.data,
                        password=hashed_password, email=form.email.data)

            db.session.add(user)

            db.session.commit()
            flash(f'Your account has been created you can now login!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Admission Number and DOB does not match', 'fail')

    return render_template('registerpage.html', title='Register', form=form, footer=1)


@app.route('/time-table/<stud_class>')
@login_required
def view_timetable(stud_class):
    if current_user.admission:
        df = pd.read_excel('/home/anupamkris/mnge/tt.xlsx')
        # df = pd.read_excel("/home/anupamkris/mnge/offline_assignment")
        for i in list(df.values):
            if i[0] == stud_class:
                fpl = i[1::2]
                spl = i[2::2]
                return render_template('timetable.html', fpl=fpl, spl=spl, stud_class=stud_class)


@app.route('/tregister', methods=['GET', 'POST'])
def tregister():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            # os.remove(
            # f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
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
        # global client
        # spreadsheet = client.open('teachers')
        # worksheet = spreadsheet.worksheet('Sheet1')
        # teacherdetails = [str(name), str(email), str(subject), str(classes), str(classteacherof)]
        # worksheet.insert_row(teacherdetails,2)
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n', securitykey, name,
              password, confirmpassword, email, subject, classes)
        teacher = Teacher.query.filter_by(email=email).first()

        if securitykey != 'qwertyuiop':
            flash("Security Key is Not Correct", 'fail')
        elif teacher != None:
            flash('Email already registered', 'fail')
        elif password != confirmpassword:
            flash("Passwords and confirm password doesn't match", 'fail')
        if teacher == None and password == confirmpassword and securitykey == 'qwertyuiop':

            hashed_password = bcrypt.generate_password_hash(
                password).decode('utf-8')

            user = User(name=name, password=hashed_password, email=email)

            db.session.add(user)

            db.session.commit()
            teacher = Teacher(name=name, email=email, classeshandled=str(
                classes), classteacher=classteacherof, subject=subject)
            db.session.add(teacher)
            db.session.commit()
            flash(f'Your account has been created you can now login!', 'success')
            return redirect(url_for('tlogin'))
        else:
            return render_template('tregister.html', title='Teacher Register', footer=1)
    else:
        return render_template('tregister.html', title='Teacher Register', footer=1)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(admission=form.admission.data).first()
        if not user:
            flash("This admission isn't registered. Please try registering.", 'fail')
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('user_home'))
        elif bcrypt.check_password_hash(user.password, form.password.data) == False:
            flash('Entered password is wrong. Please try again.', 'fail')
    return render_template('login.html', form=form, title='Student Login', footer=1)


@app.route('/tlogin', methods=['GET', 'POST'])
def tlogin():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = TeacherLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("This email isn't registered. Please try registering.", 'fail')
        elif user.admission:
            flash("This email isn't registered. Please try registering.", 'fail')
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('user_home'))
        elif bcrypt.check_password_hash(user.password, form.password.data) == False:
            flash('Entered password is wrong. Please try again.', 'fail')
    return render_template('tlogin.html', form=form, title='Faculty Login', footer=1)


@app.route('/about')
def about():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    return render_template('about.html', title='About', footer='haello')


@app.route('/contact')
def contact():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    return render_template('contact.html', title='Contact', footer='lol')


@app.route('/pricing')
def pricing():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    return render_template('pricing.html', title='Pricing')


@app.route('/user-home', methods=['GET', 'POST'])
@login_required
def user_home(circmess=None, ):
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    global current_user
    global client
    circularsheet = client.open('circular')
    studentcirculars = circularsheet.worksheet('student')
    student_circular_messages = studentcirculars.get_all_values()[::-1]
    teachercirculars = circularsheet.worksheet('teacher')
    teacher_circular_messages = teachercirculars.get_all_values()[::-1][:10]
    if request.method == 'POST':
        teacher_circular_message = request.form.get('teacher_circular_message')
        student_circular_message = request.form.get('student_circular_message')
        if teacher_circular_message:
            teachercirculars.insert_row(
                [current_user.name, teacher_circular_message], index=1)
        elif student_circular_message:
            classes = request.form.get('circular_class')
            studentcirculars.insert_row(
                [current_user.name, classes, student_circular_message], index=1)
        return redirect(url_for('user_home'))
    else:
        if not current_user.name:
            global fullstudentdata
            global s_adm
            global fields

            current_student = {}
            row = list(fullstudentdata.loc[fullstudentdata['admission'] == int(
                current_user.admission)].values[0])
            for i in range(5):
                current_student[fields[i]] = row[i]
            scm = []
            count = 0
            for i in student_circular_messages:
                if (i[1] == str(current_student['class']) + ' ' + current_student['section'] or i[1] == 'All') and count < 11:
                    scm.append(i)
                    count += 1
            print('\n\n Stud Data', current_student)

            return render_template('user-home.html', title='Profile', user=current_user, choice=choice, student=current_student, student_circular_messages=student_circular_messages, str=str)
        else:
            current_teacher = Teacher.query.filter_by(
                email=current_user.email).first()
            print(current_teacher)

            return render_template('t-user-home.html', title='Profile', user=current_user, choice=choice, teacher=current_teacher, eval=eval, len=len, student_circular_messages=student_circular_messages, teacher_circular_messages=teacher_circular_messages)


@app.route('/home-assignment', methods=['GET', 'POST'])
@login_required
def home_assignment():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    global fullstudentdata
    global s_adm
    global fields
    if not current_user.name:
        # Fetching current student details from EXCEL
        current_student = {}
        row = list(fullstudentdata.loc[fullstudentdata['admission'] == int(
            current_user.admission)].values[0])
        for i in range(5):
            current_student[fields[i]] = row[i]
        # Fetching current student's test details from GOOGLESHEETS
        tests = client.open('tests')
        testsheet = tests.worksheet('testsheet')
        classes = testsheet.col_values(2)
        student_tests = []
        s_class = str(current_student['class'])+' '+current_student['section']
        for i in range(len(classes)):
            if classes[i] == s_class:
                row = testsheet.row_values(i+1)
                student_tests.append(row)
        # fetching list of admissions submitted
        submitted_admno = {}
        for test in student_tests:
            submitted_admno[test[2]] = [sub['admno'] for sub in eval(test[4])]
        print('\n\n\n\n\n', 'Classes:', classes, '\n\n\n\n\n')
        print('\n\n\n\n\n', 'Class:', s_class, '\n\n\n\n\n')
        print('\n\n\n\n\n', 'Tests:', student_tests, '\n\n\n\n\n')
        print('\n\n\n\n\n', 'Submits', submitted_admno, '\n\n\n\n\n')

        return render_template('s-home-assignment.html', student=current_student, student_tests=student_tests, str=str, int=int, eval=eval, sub_admno=submitted_admno)
    else:
        # Getting current teacher details
        current_teacher = Teacher.query.filter_by(
            email=current_user.email).first()
        # Fetching current teacher's test details
        tests = client.open('tests')
        testsheet = tests.worksheet('testsheet')
        emails = testsheet.col_values(1)
        teacher_tests = []
        for i in range(len(emails)):
            if emails[i] == current_user.email:
                row = testsheet.row_values(i+1)
                teacher_tests.append(row)
        # loading the teacher's classes' strength
        Class = list(fullstudentdata['class'])
        section = list(fullstudentdata['section'])
        for i in range(len(Class)):
            Class[i] = str(Class[i])+' '+section[i]
        strength = {}
        for i in eval(current_teacher.classeshandled):
            strength[i] = Class.count(i)
        if teacher_tests:
            print('\n\n\n\n\n', teacher_tests, '\n\n\n\n\n\n')
        else:
            print('\n\n\n\n\n\n\n\nNo tests yet\n\n\n\n\n\n')
        # fetching list of marks of tests
        submitted_marks = {}
        for test in teacher_tests:
            submitted_marks[test[2]] = [
                str(sub['marks']) for sub in eval(test[4])]
        # print('\n\n\n\n\n','Class:',Class,'\n\n\n\n\n')
        # print('\n\n\n\n\n','Strength:',strength,'\n\n\n\n\n')
        print('\n\n\n\n\n', 'marks:', submitted_marks, '\n\n\n\n\n')

        return render_template('t-home-assignment.html', teacher=current_teacher, teacher_tests=teacher_tests, strength=strength, sub_marks=submitted_marks, eval=eval, len=len, str=str)


@app.route('/view-details/<testname>', methods=['GET', 'POST'])
@login_required
def view_assignment_details(testname=None):
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    if current_user.name:
        if testname:
            current_teacher = Teacher.query.filter_by(
                email=current_user.email).first()
            global fullstudentdata
            global client
            tests = client.open('tests')
            testsheet = tests.worksheet('testsheet')
            testnames = testsheet.col_values(3)
            for i in testnames:
                if i == testname:
                    current_test = testsheet.row_values(testnames.index(i)+1)
                    break
            test_class = current_test[1]

            Class = list(fullstudentdata['class'])
            section = list(fullstudentdata['section'])
            for i in range(len(Class)):
                Class[i] = str(Class[i])+' '+section[i]
            name = list(fullstudentdata['name'])
            admno = list(fullstudentdata['admission'])
            student_details = {}  # u there? See, now we gotta create a folder with the name of the test to save the student's answer paper eaxh time
            student_list = []
            # what dows this fucntion do??
            print(
                f'\n\n\n\n\nClass{Class}{len(Class)}\n\n\nname{name}{len(name)}\n\n')
#which function? view_assignment_details? yeah:... it collecsts the student info from the class to which the test is assigned and passes that data to the view_assignment_details render render_template#
# so we'll make a nwe route for downloading or for the embed page, just pass the testname and student admno as vars for urlfor('pdf_viewer', testname = '', admno = '')?got it
# for showing the table of students who finishhed and who didnt finish
            for i in range(len(Class)):
                print(i)
                if Class[i] == test_class:
                    # 	print(i, name[i])
                    # 	print(i, Class[i])
                    # 	print(i, admno[i])
                    # student_details['name'] = name[i]
                    # student_details['class'] = Class[i]
                    # student_details['admno'] = admno[i]
                    student_details = {'name': name[i],
                                       'class': Class[i], 'admno': admno[i], }
                    student_list.append(student_details)
            sub_adm = []
            sub_adm = [str(sub['admno']) for sub in eval(current_test[4])]
            notsub_count = len(student_list) - len(sub_adm)
            for student in student_list:
                if str(student['admno']) in sub_adm:
                    print('\n\n\n\n\n\n', current_test)
                    print(f'\n\n\n\n', eval(current_test[4])[sub_adm.index(
                        str(student['admno']))]['link'], '\n\n\n\n\n\n')

            return render_template('t-view-ass-details.html', student_list=student_list, current_test=current_test, sub_adm=sub_adm, eval=eval, str=str, len=len, render_template=render_template)
    else:
        return redirect(url_for('user_home'))


@app.route('/pdf-viewer/<testname>/<admno>/<mark>', methods=['GET', 'POST'])
@login_required
def pdf_viewer(testname=None, admno=None, mark=None):
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    if current_user.name:
        if request.method == 'POST':
            # input field name?? and submit_marks is the submit
            marks = request.form.get('marks')
            remark = request.form.get('remark')
            # i didnt read it
            tests = client.open('tests')
            testsheet = tests.worksheet('testsheet')
            testname1 = testsheet.col_values(3)
            for i in range(len(testname1)):
                if testname1[i] == testname:
                    row = testsheet.row_values(i+1)
                    rowindex = i+1
                    break
            submitteddata = eval(row[4])  # this is python indexing
            # dd = {}
            # #!!dict['marks'] is the key for marks of the student
            # # dict['admno'] is admno right?? ok
            # exec(f'datalist = {submitteddata}')
            # datalist = dd['datalist']
            # for i in range(len(datalist)):
            #     if datalist[i]['admno'] == admno:
            #         datalist[i]['marks'] = marks
            #         break
            for i in submitteddata:
                if i['admno'] == admno:
                    i['marks'] = marks
                    i['remark'] = remark
            print('\n\n\n\n\nDATA', marks, '\n\n\n\n\n')
            testsheet.update_cell(rowindex, 5, str(submitteddata))
            # os.remove(f'{testname}{admno}.pdf')
            return redirect(url_for('view_assignment_details', testname=testname))
            s_class = str(current_student['class']) + \
                ' '+current_student['section']
        else:
            mclient = MediaFireClient()
            mclient.login(email='media.mngeforhvf@gmail.com',
                          password='hard2reach', app_id='42511')
            mclient.download_file(f"mf:/{testname}/{admno}.pdf",
                                  f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{testname}{admno}.pdf")
            loc = f'{testname}{admno}.pdf'
            filename = testname+admno+'.pdf'
            session['filename'] = filename
            if mark == 'None':
                mark = None
    # =======

    # >>>>>>> 85143769cf2966a4709fe1bfd0209960da6eee1e
            return render_template('embedpdf.html', filename1='answersheets/'+filename, footer='hah', mark=mark)
    else:
        # got it
        return redirect(url_for('user_home'))


@app.route('/downloadfile/<testname>')
def downloadfile(testname):
    client = MediaFireClient()
    client.login(email='media.mngeforhvf@gmail.com',
                 password='hard2reach',
                 app_id='42511')
    link = client.get_direct_download_link(f'mf:/{testname}/QP.pdf')
    return redirect(link)


@app.route('/create-assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    if current_user.name:
        current_teacher = Teacher.query.filter_by(
            email=current_user.email).first()
        if request.method == 'POST':
            filename = request.form.get('testname')
            global client
            worksheet = client.open('tests')
            testsheet = worksheet.worksheet('testsheet')
            testnames = testsheet.col_values(3)
            for test in testnames:
                if filename == test:
                    flash('Test Name already exists please use another name', 'fail2')
                    return render_template('create-assignment.html', teacher=current_teacher, eval=eval)
            for i in range(10):
                try:
                    f = request.files['qpupload']
                except:
                    try:
                        f = request.files.getlist('imgupload')
                    except:
                        f = None
                if f:
                    # Why pink!
                    # okay
                    f.save('QP.pdf')
                    createfolder(filename)
                    link = uploadfile('QP.pdf', filename)
                    break

                elif f:
                    file = open("server.log", 'a')
                    dellist = []
                    for j in range(len(f)):
                        f = request.files.getlist('imgupload')
                        f[j].save(current_user.name.split()[0]+str(j)+'.jpg')
                        dellist.append(current_user.name.split()
                                       [0]+str(j)+'.jpg')
                        file.write(dellist[j])
                    for j in dellist:
                        img = Image.open(j)
                        w, h = img.size
                        w, h = int(w/3), int(h/3)
                        img = img.resize((w, h))
                        img.save(j)
                    with open('QP.pdf', 'wb') as pdffile:
                        pdffile.write(img2pdf.convert(dellist))
                    for j in dellist:
                        os.remove(j)
                    createfolder(filename)
                    link = uploadfile('QP.pdf', filename)
                    break
                else:
                    flash("You must choose atleast one type of file", 'fail2')
                    return redirect(url_for('create_assignment'))
            testsheet = client.open('tests')
            worksheet = testsheet.worksheet('testsheet')
            datalist = [current_user.email, request.form.get(
                'class'), filename, link, '[]']
            worksheet.insert_row(datalist, 2)
            flash('Assignment created Successfully!', 'success2')
            os.remove('QP.pdf')
            return redirect(url_for('home_assignment'))
        else:
            return render_template('create-assignment.html', teacher=current_teacher, eval=eval)
    else:
        return redirect(url_for('user_home'))


@app.route('/submit-assignment/<testname>', methods=['GET', 'POST'])
@login_required
def submit_assignment(testname=None):
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    if not current_user.name:
        if request.method == 'POST':
            global client
            spreadsheet = client.open('tests')
            worksheet = spreadsheet.worksheet('testsheet')
            fulldata = worksheet.get_all_values()
            print(
                '\n\n\n\n\n\n\n\n\n\n_________________________________n\\n\n\n\n\n\n\n\n\n\n\n')
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
                                print(
                                    '\n\n\n\n\n\n\n\n Already Submitted you fool! \n\n\n\n\n\n\n\n')
                                return render_template('register.html')
                        else:
                            for retry in range(10):
                                try:
                                    f = request.files['pdfupload']
                                except:
                                    f = None
                                if f:
                                    f.save(''+current_user.admission+'.pdf')
                                    link = uploadfile(
                                        current_user.admission+'.pdf', testname)
                                    print('running else')
                                    updata.append(
                                        {'admno': current_user.admission, 'link': link, 'marks': None, 'remarks': None})
                                    worksheet.update_cell(i+1, 5, str(updata))
                                    break
                                else:
                                    f = request.files.getlist('imgupload')
                                    file = open("server.log", 'a')
                                    dellist = []
                                    for j in range(len(f)):
                                        f[j].save(
                                            current_user.admission+str(j)+'.jpg')
                                        dellist.append(
                                            current_user.admission+str(j)+'.jpg')
                                        file.write(dellist[j])
                                    for j in dellist:
                                        img = Image.open(j)
                                        w, h = img.size
                                        w, h = int(w/3), int(h/3)
                                        img = img.resize((w, h))
                                        img.save(j)
                                    with open(current_user.admission+'.pdf', 'wb') as pdffile:
                                        pdffile.write(img2pdf.convert(dellist))
                                    for j in dellist:
                                        os.remove(j)
                                    link = uploadfile(
                                        current_user.admission+'.pdf', testname)
                                    print('running else')
                                    updata.append(
                                        {'admno': current_user.admission, 'link': link, 'marks': None, 'remarks': None})
                                    worksheet.update_cell(i+1, 5, str(updata))
                                    break
                    except:
                        try:
                            f = request.files['pdfupload']
                        except:
                            f = None
                        if f:
                            f.save(''+current_user.admission+'.pdf')
                            link = uploadfile(
                                current_user.admission+'.pdf', testname)
                            print('running except')
                            updata.append(
                                {'admno': current_user.admission, 'link': link, 'marks': None, 'remarks': None})
                            print(updata)
                            worksheet.update_cell(i+1, 5, str(updata))
                        else:
                            f = request.files.getlist('imgupload')
                            file = open("/home/mngeforkvhvf/server.log", 'a')
                            file.write('Filelist : '+str(f))
                            dellist = []
                            for j in range(len(f)):
                                f[j].save(current_user.admission+str(j)+'.jpg')
                                file.write(str(j))
                                dellist.append(
                                    current_user.admission+str(j)+'.jpg')
                                file.write(dellist[j])
                            file.write(str(dellist))
                            for j in dellist:
                                img = Image.open(j)
                                w, h = img.size
                                w, h = int(w/3), int(h/3)
                                img = img.resize((w, h))
                                img.save(j)
                            with open(current_user.admission+'.pdf', 'wb') as pdffile:
                                pdffile.write(img2pdf.convert(dellist))
                            for j in dellist:
                                os.remove(j)
                            link = uploadfile(
                                current_user.admission+'.pdf', testname)
                            print('running else')
                            updata.append(
                                {'admno': current_user.admission, 'link': link, 'marks': None, 'remarks': None})
                            worksheet.update_cell(i+1, 5, str(updata))
                            break
            os.remove(current_user.admission+'.pdf')
            flash('Assignment Submitted!', 'success2')
            return redirect(url_for('home_assignment'))
        else:
            global fullstudentdata
            global s_adm
            global fields
            current_student = {}
            row = list(fullstudentdata.loc[fullstudentdata['admission'] == int(
                current_user.admission)].values[0])
            for i in range(5):
                current_student[fields[i]] = row[i]
            return render_template('submit-assignment.html', student=current_student, eval=eval, str=str)


@app.route('/resultpage/<testname>/<admission>')
def resultpage(testname=None, admission=None):
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    global client
    worksheet = client.open('tests')
    testsheet = worksheet.worksheet('testsheet')
    testnames = testsheet.col_values(3)
    for i in range(len(testnames)):
        if testnames[i] == testname:
            row = testsheet.row_values(i+1)
            rowindex = i+1
            break
    for i in eval(row[4]):
        if i['admno'] == admission:
            mark = i['marks']
            remark = i['remark']
    return render_template('resultpage.html', mark=mark, remark=remark, testname=testname)


@app.route('/logout')
def logout():
    try:
        if session['filename']:
            os.remove(
                f"/home/anupamkris/mnge/offline_assignment/assignment/static/answersheets/{session['filename']}")
            session['filename'] = ''
    except:
        pass
    logout_user()
    return redirect(url_for('home'))


@app.route('/online-tests')
def online_test():
    if not current_user.name:
        return render_template('s-onlinetests.html', title='Online Tests')
    else:
        current_teacher = Teacher.query.filter_by(
            email=current_user.email).first()
        global client
        worksheet = client.open('onlinetests')
        testsheet = worksheet.worksheet('testsheet')
        emails = testsheet.col_values(1)
        teacher_tests = []
        for i in range(len(emails)):
            if emails[i] == current_user.email:
                row = testsheet.row_values(i+1)
                teacher_tests.append(row)
        return render_template('t-onlinetest.html', title='Online Tests')


@app.route('/create-test', methods=['GET', 'POST'])
def create_test():
    if not current_user.name:
        return redirect('user_home', title='Profile')
    else:
        current_teacher = Teacher.query.filter_by(
            email=current_user.email).first()
        if request.method == 'POST':
            filename = request.form.get('testname')
            global client
            worksheet = client.open('tests')
            testsheet = worksheet.worksheet('testsheet')
            testnames = testsheet.col_values(3)
            for test in testnames:
                if filename == test:
                    flash('Test Name already exists please use another name', 'fail2')
                    return render_template('create-test.html', teacher=current_teacher, eval=eval)
            for i in range(10):
                try:
                    f = request.files['qpupload']
                except:
                    try:
                        f = request.files.getlist('imgupload')
                    except:
                        f = None
                if f:
                    # Why pink!
                    # okay
                    f.save('QP.pdf')
                    createfolder(filename)
                    link = uploadfile('QP.pdf', filename)
                    break
                elif f:
                    file = open("server.log", 'a')
                    dellist = []
                    for j in range(len(f)):
                        f = request.files.getlist('imgupload')
                        f[j].save(current_user.name.split()[0]+str(j)+'.jpg')
                        dellist.append(current_user.name.split()
                                       [0]+str(j)+'.jpg')
                        file.write(dellist[j])
                    for j in dellist:
                        img = Image.open(j)
                        w, h = img.size
                        w, h = int(w/3), int(h/3)
                        img = img.resize((w, h))
                        img.save(j)
                    with open('QP.pdf', 'wb') as pdffile:
                        pdffile.write(img2pdf.convert(dellist))
                    for j in dellist:
                        os.remove(j)
                    createfolder('onlinetest/'+filename)
                    link = uploadfile('QP.pdf', 'onlinetest/'+filename)
                    break
                else:
                    flash("You must choose atleast one type of file", 'fail2')
                    return redirect(url_for('create_test'))
            testsheet = client.open('onlinetests')
            worksheet = testsheet.worksheet('testsheet')
            datalist = [current_user.email,
                        request.form.get('class'),
                        filename, request.form.get('qpnos'),
                        request.form.get('testtimeduration'),
                        request.form.get('teststartdate') +request.form.get('teststarttime'),
                        request.form.get('testenddate') +request.form.get('testendtime'),
                        link, '[]']
            worksheet.insert_row(datalist, 2)
            flash('Assignment created Successfully!', 'success2')
            os.remove('QP.pdf')
            return redirect(url_for('online_test'))
        else:
            return render_template('create-test.html', teacher=current_teacher, eval=eval)
