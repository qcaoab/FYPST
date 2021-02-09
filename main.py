import os
import string
from uuid import uuid4
import urllib.request

from flask import Flask, flash, request, redirect, url_for, render_template,send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#location = 'C:/Users/qlcql/Documents/GitHub/FYPST'

app = Flask(__name__,template_folder='templates/')
app.static_folder = 'static'
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def home():
    return render_template('empty.html')

@app.route('/empty')
def empty():
    return render_template('empty.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/gallary',methods=['GET','POST'])
def gallary():
    return render_template('gallary.html')

@app.route('/upload/<item>', methods=['GET','POST'])
def select():
    item = request.form.get("dropdown-large")
    return render_template('upload.html', item = item)

@app.route('/upload/<filename>', methods=['GET','POST'])
def upload_image():
            
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['./pics/upload'], filename))
        print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed')
        return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return render_template('upload.html')

@app.route('/upload/<filename>')
def send_file(filename):
    return send_from_directory('../pic/uploads/', filename)

@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='../pic/uploads/' + filename), code=301)

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
    