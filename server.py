import os
import subprocess

from uuid import uuid4
import urllib.request
from pathlib import Path
import ntpath
from flask import Flask, flash, request, redirect, url_for, render_template,send_from_directory, session
from werkzeug.utils import secure_filename

import Arbitrary_ST_Pytorch
from Arbitrary_ST_Pytorch.test import arbi_trans

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#location = 'C:/Users/qlcql/Documents/GitHub/FYPST'

app = Flask(__name__,template_folder='templates')
# the directory for cnn
app.config["IMAGE_UPLOADS_C"] = "static/pics/uploads/content"
app.config["IMAGE_UPLOADS_S"] = "static/pics/uploads/style"

# the directory for cyclegan
app.config["IMAGE_UPLOADS_G"] = "cyclegan/uploads"

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
    
    gan_style = {
        "monet": "monet_cyclegan",
        "vangogh": "vangogh_cyclegan"
        # add more later
    }

    if request.method == 'POST':

        style = request.form.get('style_select')

        if 'file' not in request.files:
            flash('Attention: No file part','danger')
            return redirect(request.url)
        file = request.files['file']

        if str(style) == 'blank':
            flash('Please choose a valid style reference from the drop-down list', 'danger')
            print("invalid")
            return redirect(request.url)

        if file.filename == '':
            flash('Attention: No image selected for uploading', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('----------------------------allowed')
            filename = secure_filename(file.filename)
            folder = '/' + filename.rsplit('.', 1)[0]
            
            # create a folder with the same name as the uploaded image, and save the image in that folder
            if not os.path.exists(app.config["IMAGE_UPLOADS_G"]+folder):
                os.makedirs(app.config["IMAGE_UPLOADS_G"]+folder)

            # path of test folder
            file.save(os.path.join(app.config["IMAGE_UPLOADS_G"]+folder, filename))

            test_path = 'uploads'+folder

            flash('Successfully uploaded', 'info')
            print('using style: '+str(style))
            print('using model: '+gan_style[style])

            # run test.py
            print(os.getcwd())
            os.chdir(os.getcwd()+"/cyclegan")
            cmd = "python test.py --dataroot "+test_path+" --name "+gan_style[style]+" --gpu_ids -1 --results_dir ../static/results --model test --no_dropout"
            subprocess.check_call(cmd)
            os.chdir(os.path.split(os.getcwd())[0])

            resultpath = 'static/results/'+gan_style[style]+'/test_latest/images/'+filename.rsplit('.', 1)[0]+'_fake.png'
            print(resultpath)

            return render_template('upload.html', file = file, resultpath = resultpath)
        else:
            flash('Attention: Allowed image types are -> png, jpg, jpeg, gif', 'danger')
            return redirect(request.url)
    else:
        return render_template('upload.html')


@app.route('/upload2', methods=['GET','POST'])
def upload2():

    if request.method == 'POST':
        print("start uploading ...")
    
        degree = request.form.get('degree')
        preserve = request.form.get('preserve')
        
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('Attention: No file part', 'danger')
            return redirect(request.url)
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            flash('Attention: Need to select two pictures', 'danger')
            return redirect(request.url)
        
        if allowed_file(file1.filename)==False or allowed_file(file2.filename)==False:
            flash('Error: Allowed image types are -> png, jpg, jpeg, gif', 'danger')
            return redirect(request.url)
        
        else:
      
            filename1 = secure_filename(file1.filename)
            path1 = os.path.join(app.config["IMAGE_UPLOADS_C"], filename1)
            file1.save(path1)
            flash('Uploaded content image: ' + filename1, 'info')
      
          
            filename2 = secure_filename(file2.filename)
            path2=os.path.join(app.config["IMAGE_UPLOADS_S"], filename2)
            print('----------------------')
            print(path1)
            print(path2)
            file2.save(path2)
            flash('Uploaded style image: ' + filename2, 'info')
            print('transfer starts')
            degree = float(degree)/100
            resultname = arbi_trans(path1, path2,preserve_color= bool(int(preserve)), alpha = float(degree))
            
            #resultpath=os.path.abspath(resultname)
            resultpath = str(resultname).replace('\\','/')
            
            flash('select degree = ' + str(degree), 'info')
            flash('preserve color = ' + str(preserve), 'info')

            print(resultpath)
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
