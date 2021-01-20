import os
from taskscheduler2 import *
from flask import Flask, request, jsonify,render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
ALLOWED_EXTENSIONS = ['py', 'pyc', 'R', 'sql', 'c']


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
        return 'Uploaded '+ ', '.join(filenames) +' for ' + project


    print(project)
    return project + ' file uploaded successfully'
		
if __name__ == '__main__':
   app.run(debug = True)