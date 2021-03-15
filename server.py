import os

from uuid import uuid4
import urllib.request
from pathlib import Path

from flask import Flask, flash, request, redirect, url_for, render_template,send_from_directory, session
from werkzeug.utils import secure_filename

import Arbitrary_ST_Pytorch
from Arbitrary_ST_Pytorch.test import arbi_trans

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#location = 'C:/Users/qlcql/Documents/GitHub/FYPST'

app = Flask(__name__,template_folder='templates')
#app.config["IMAGE_UPLOADS"] = "/FYPST/static/img/uploads"
app.config["IMAGE_UPLOADS_C"] = "static/pics/uploads/content"
app.config["IMAGE_UPLOADS_S"] = "static/pics/uploads/style"
app.config["IMAGE_UPLOADS_G"] = "static/pics/uploads/gan"

app.static_folder = 'static'

app.config['SECRET_KEY'] = "FYPST_secret"

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

@app.route('/style/genre/'+'<genre>')
def style(genre):
    return render_template('style.html', genre = genre)

@app.route('/upload', methods=['GET','POST'])

def upload():
    if request.method == 'POST':
        

        if 'file' not in request.files:
            flash('Attention: No file part','danger')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('Attention: No image selected for uploading', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('----------------------------allowed')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["IMAGE_UPLOADS_G"], filename))
            flash('Successfully uploaded', 'info')
            #nn(item, filename)
            return render_template('upload.html', file = file)
        else:
            flash('Attention: Allowed image types are -> png, jpg, jpeg, gif', 'danger')
            return redirect(request.url)
    else:
        return render_template('upload.html')

################### select testing
@app.route('/test', methods=['GET', 'POST'])

def select_style():
    if request.method == 'POST':
        select = request.form.get('style_select')
        return(str(select)) # just to see what select is
    else:
        return render_template(
        'select.html',
        data=[{'name':'monet'}, {'name':'vangogh'}, {'name':'ukiyoe'}, {'name':'edgar'}])

###################################



@app.route('/upload2', methods=['GET','POST'])
def upload2():

    if request.method == 'POST':
        print("start uploading ...")
    
        
        
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('Attention: No file part')
            return redirect(request.url)
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            flash('Attention: Need to select two pictures', 'danger')
            return redirect(request.url)
        
        if allowed_file(file1.filename)==False or allowed_file(file2.filename)==False:
            flash('Error: Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)
        
        else:
      
            filename1 = secure_filename(file1.filename)
            path1 = os.path.join(app.config["IMAGE_UPLOADS_C"], filename1)
            file1.save(path1)
            flash('Uploaded content image: ' + filename1)
      
          
            filename2 = secure_filename(file2.filename)
            path2=os.path.join(app.config["IMAGE_UPLOADS_S"], filename2)
            print('----------------------')
            print(path1)
            print(path2)
            file2.save(path2)
            flash('Uploaded style image: ' + filename2)
            print('transfer starts')
            resultname = arbi_trans(path1, path2, filename1, filename2)
            resultpath = Path(resultname)
            print('function called')
            print(resultname)
            #result.save(os.path.join(app.config["static/pics/uploads"], 'transfer_result.jpg'))
        return render_template('upload2.html', file1 = file1, file2=file2, resultpath = resultpath)
       
    else:
        return render_template('upload2.html')



###################for testing

#put the constant directory to the beginning

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
