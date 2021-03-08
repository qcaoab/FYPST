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
@app.route('/style/genre/'+'<genre>')
def style(genre):
    return render_template('style.html', genre = genre)

@app.route('/upload', methods=['GET','POST'])
def upload():
    return render_template("upload.html")

def create_upload():
    if request.method == 'POST':
        
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['pics/upload/'], filename))
            print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed')
            #nn(item, filename)
            return render_template('upload.html', file = file)
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
    else:
        return render_template('upload.html')
'''
@app.route('/upload/<filename>')
def uploadpic(filename):
    return render_template('upload.html', pics=get_last_pics(), filename = pics.filename)
'''
@app.route('/upload2', methods=['GET','POST'])
def upload2():
    return render_template("upload2.html")
def create2_upload():
    if request.method == 'POST':
        print("start uploading ...")
        '''
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        '''
        file = request.files['file1']
        '''
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
        '''
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['static/pics/upload/'], filename))
        print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed')
            #nn(item, filename)
        
        return render_template('upload.html', file = file)
        '''
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
        '''
    else:
        return render_template('upload2.html')
    
    

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

###################for testing

app.config["IMAGE_UPLOADS"] = "/FYPST/static/img/uploads"

@app.route('/upload-image', methods=['GET','POST'])
def upload_image():
    if request.method == "POST":

        if request.files:
            image = request.files["image"]
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            print("image saved")
            return redirect(request.url)
    return render_template("upload_image.html")

##########################

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
    