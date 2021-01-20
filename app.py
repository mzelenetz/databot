from flask import Flask, render_template, redirect, request, url_for, flash
import pyodbc
from werkzeug.exceptions import abort
import re
import os
import shutil
import subprocess
from taskscheduler2 import *
import datetime
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = ['py', 'pyc', 'R', 'sql', 'c']

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# get column names in dict
#    dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()

def get_db_connection():
    conn = pyodbc.connect('DRIVER={SQL SERVER};SERVER=DRTUAT01JUP01;Trusted_Connection=yes;')
    return conn.cursor()

def clean_email(emails):
    emails = emails.replace(' ', '')
    emails = re.split(',|;', emails)
    return emails

def task_exists(project):
    """
    check if the task exists
    """
    task_info = info(project)
    try:
        task_info['enabled']
        return True
    except:
        return False

def list_project_tasks():
    projects = get_list_project_names()
    tasks = list_tasks()
    active_project_tasks = list(set(projects) & set(tasks))
    return active_project_tasks

def get_task_info(project):
    return info(project)

def create_path(project):
    base_path = os.path.abspath(os.getcwd())
    base_path += '\\' + project + '\\'
    return base_path


def get_project(project):
    """
    given the Project Name, get the details
    """
    con = get_db_connection()
    result = con.execute("select report, reportDescription, createdwhen, CASE WHEN modifiedwhen is null THEN createdwhen ELSE modifiedwhen end as modifiedwhen from JupiterCustomData.ClincialOther.ReportDescription WHERE report = '{}'".format(project))
    project = [dict(zip([column[0] for column in result.description], row)) for row in result.fetchall()][0]
    if project is None:
        abort(404)
    return project

def get_email_list(project):
    """
    return the list of email recipients
    """
    con = get_db_connection()
    result = con.execute("select reportuserid, report, emailto, updatedby, createdwhen, CASE WHEN modifiedwhen is null THEN createdwhen ELSE modifiedwhen end as modifiedwhen from JupiterCustomData.ClincialOther.ReportDistribution WHERE report = '{}'".format(project))
    recipients = [dict(zip([column[0] for column in result.description], row)) for row in result.fetchall()]
    if recipients is None:
        abort(404)
    return recipients

def get_projects():
    con = get_db_connection()
    result = con.execute('select report, reportDescription, createdwhen, CASE WHEN modifiedwhen is null THEN createdwhen ELSE modifiedwhen end as modifiedwhen from JupiterCustomData.ClincialOther.ReportDescription')
    projects = [dict(zip([column[0] for column in result.description], row)) for row in result.fetchall()]
    con.close()
    return projects

def get_list_project_names():
    projects = get_projects()
    return [project['report'] for project in projects]

@app.route('/')
def index():
    projects = get_projects()
    return render_template('index.html', projects=projects)

@app.route('/Project/<project>')
def flask_project(project):
    report = get_project(project)
    recipients = get_email_list(project)
    task_info = get_task_info(project)
    path = create_path(project)
    if not os.path.exists(path):
        os.mkdir(path)
    files = os.listdir(path)
    return render_template('project.html', project = report , recipients = recipients , task_info = task_info, files = files)

@app.route('/Project/Schedule/<project>/<file>')
def flask_project_schedule(project, file):
    report = get_project(project)
    task_info = get_task_info(project)
    path = create_path(project)
    file_path = path + file
    return render_template('schedule.html', project = report ,task_info = task_info, filename = file,  file_path = file_path)


@app.route('/createproject', methods=['POST'])
def create_project():
    report = request.form['report']
    reportDescription = request.form['reportDescription']
    con = get_db_connection()
    con.execute("INSERT INTO JupiterCustomData.clincialother.ReportDescription (Report, ReportDescription) VALUES ('{}' , '{}')".format(report, reportDescription))
    con.commit()
    return redirect('/')

@app.route('/delete/<project>/<int:reportuserid>', methods=['POST'])
def delete_email(reportuserid, project):
    con = get_db_connection()
    con.execute("DELETE FROM JupiterCustomData.clincialother.ReportDistribution WHERE reportuserid = '{}'".format(reportuserid))
    con.commit()
    return redirect('/Project/' + project)

@app.route('/delete/file/<project>/<file>', methods=['POST'])
def delete_file(project, file):
    path = create_path(project)
    file_path = path + file
    if os.path.isdir(file_path):
        shutil.rmtree(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("Does not exist: " + str(file_path))
    return redirect('/Project/' + project)

@app.route('/insertemail', methods=['POST'])
def insert_email():
    if request.method == 'POST':
        email_raw = request.form['emailto']
        project = request.form['project']

    if not email_raw:
        flash('Email is required!')
    else:
        emails = clean_email(email_raw)
        con = get_db_connection()
        for email in emails:
            try:
                con.execute("INSERT INTO JupiterCustomData.clincialother.ReportDistribution (Report, EmailTo) VALUES ('{}' , '{}')".format(project, email))
            except:
                pass

            con.commit()
        con.close()

    return redirect('/Project/' + project)

@app.route('/taskscheduler/deletetrigger/<project>', methods = ['POST'])
def trigger_remove(project):
    clear_triggers(project)
    return redirect('/Project/' + project)


@app.route('/taskscheduler/triggernow/<project>', methods = ['POST'])
def execute_code_once(project):
    program_file_path =  request.form['file_path']
    #run the program from command line
    subprocess.call(program_file_path, shell=True)
    return redirect('/Project/' + project)


@app.route('/taskscheduler/testtrigger/<project>', methods = ['POST'])
def execute_code_test(project):
    program_file_path =  request.form['file_path']
    #run the program from command line
    os.system(program_file_path + ' --test')
    return redirect('/Project/' + project)

@app.route('/taskscheduler/addtrigger/<project>', methods = ['POST'])
def trigger_add(project):
    #repeat_interval =  request.form['repeatIntervalDD']
    trigger_type =  request.form['triggertypeDD']
    trigger_type = 'Once'

    add_trigger(project,  trigger_type=trigger_type)
    return redirect('/Project/' + project)



@app.route('/taskscheduler/addschedule/<project>', methods = ['POST'])
def schedule_add(project):
    #repeat_interval =  request.form['repeatIntervalDD']
    trigger_type =  request.form['triggertypeDD']
    days_of_week =  request.form.getlist('weekday')
    file_path =  request.form['file_path']
    startdate = request.form['startdate']
    starttime = request.form['starttime']

    if startdate is None and starttime is not None:
        startdate = datetime.strptime(datetime.now(), '%Y-%m-%d')
    elif startdate is not None and starttime is None:
        starttime = '00:00'

    start = startdate + ' ' + starttime

    # TODO: Handle this better in the future. Now there can only be one trigger at time.
    # hang on for some hacky shit
    print(project, trigger_type, days_of_week, file_path, start, startdate, starttime)
    res = create_task2(project, path=str(file_path))
    print(res)
    if trigger_type in ['Daily', 'Once']:
        clear_triggers(project)
        add_trigger(project, trigger_type=trigger_type, start_date = startdate, start_time=starttime)
    elif trigger_type == 'Weekly':
        create_task2(project, path=file_path)
        clear_triggers(project)
        add_trigger(project, trigger_type='Weekly', days_of_week = days_of_week, start_date = startdate, start_time=starttime)

    return redirect('/Project/' + project)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['POST'])
def upload_file2():
    #Get Project Name
    project = request.form['project']

    # Make the project dir if it doesn't exist
    if request.method =='POST':
        if not os.path.isdir(project):
            os.mkdir(project)
        
        uploaded_files = request.files.getlist("file[]")
        filenames = []
        # if user does not select file, browser also
        # submit a empty part without filename
        for file in uploaded_files:
            if file: #and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(project, filename))
                filenames.append(filename)
            flash('Upload Success')
        return redirect('/Project/' + project)


    return redirect('/Project/' + project)

@app.route('/listfiles')
def list_exe(project):
    exe = request.form['exe']
    path = create_path(project)
    return os.listdir(path)
    

def delete_project_sql(project):
    con = get_db_connection()
    con.execute("DELETE FROM JupiterCustomData.clincialother.ReportDistribution WHERE report = '{}'".format(project))
    con.execute("DELETE FROM JupiterCustomData.clincialother.ReportDescription WHERE report = '{}'".format(project))
    con.commit()
    return True

@app.route('/delete/project/<project>', methods = ['POST'])
def delete_project(project):
    """
    Delete the whole project
    """
    #delete tasks
    delete_task(project)

    #Delete the files
    path = create_path(project)
    files = os.listdir(path)
    for file in files:
        delete_file(project, file)

    #remove from emails
    delete_project_sql(project)
    return redirect('/')

    

	


"""
@app.route('/<project>/delete/<emailto>', methods=['DELETE'])
def delete_email(project, emailto):
    con = get_db_connection()
    con.execute("DELETE FROM JupiterCustomData.clincialother.ReportDistribution WHERE Report = '{}' and Emailto = '{}'".format(project, emailto))
    return flask_project(project)
"""
