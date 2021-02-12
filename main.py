import os

from uuid import uuid4
import urllib.request


from flask import Flask, flash, request, redirect, url_for, render_template,send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#location = 'C:/Users/qlcql/Documents/GitHub/FYPST'

app = Flask(__name__,template_folder='templates')

app.static_folder = 'static'
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_last_pics():
    try:
        cur = g.db.execute('select filename, label from pics order by id desc limit 25')
        filenames = []
        for row in cur.fetchall():
            filenames.append({"filename": row[0], "label": row[1] or ''})
        return filenames
    except:
        return []

	
@app.route('/')
def home():
    return render_template('empty.html')


@app.route('/empty')
def empty():
    return render_template('empty.html')

@app.route('/gallery',methods=['GET','POST'])
def gallery():
    return render_template('gallery.html')
'''
@app.route('/upload')
def upload():
    return render_template('upload.html')
'''
@app.route('/style/<stylename>')
def style(stylename):
    return render_template('style.html', stylename = stylename)

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        item = request.form.get("dropdown-large")
             
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['./pics/upload/'], filename))
            print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed')
            #nn(item, filename)
            return render_template('upload.html', filename) 
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
    else:
        return render_template('upload.html')
'''
@app.route('/upload/<filename>')
def uploadpic(filename):
    return render_template('upload.html', pics=get_last_pics(), filename = pics.filename)
'''
@app.route('/upload/show')
def show_pic():
    filename = request.args.get('filename', '')
    t = (filename,)
    cur = g.db.execute('select label from pics where filename=?', t)
    label = cur.fetchone()[0]
    
    return render_template('upload.html', filename=filename, label=label)

@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='../pic/uploads/' + filename), code=301)

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
    