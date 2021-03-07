from flask import Flask
from flask import jsonify, request

import csv
from datetime import datetime
from io import StringIO
from werkzeug.wrappers import Response
app = Flask(__name__)

UPLOAD_FOLDER = 'pic/uploads/'
answers = dict()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route("/api/answers", methods=['GET'])
def get_answer():
	question = request.args.get('question')
    with open('db.json','r') as db_read:
        answers = json.load(db_read)
	if question in answers:
		return jsonify({"status": 200, "answer": answers[question]})
	else:
		return jsonify({"status": 404, "message": "No answer."})

@app.route("/api/answers", methods=['POST'])
def post_answer():
	data = request.get_json()
	question = str(data["question"])
	answer = str(data["answer"])
	answers[question] = answer
    with open('db.json', 'r') as db_read:
		data = json.load(db_read)
	with open('db.json', 'w') as db_write:
		data[question] = answer
		json.dump(data, db_write)
	
	return jsonify({"question": question, "answer": answer})


@app.route("/answers", methods=['GET'])
def render_answer():
	question = request.args.get('question')
	with open('db.json', 'r') as db_read:
		answers = json.load(db_read)
	if question in answers:
		# Make sure to also import render_template from flask in the imports above!
		return render_template("answer.html", question=question, answer=answers[question])
	else:
		return jsonify({"status": 404, "message": "No answer."})

@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>Transform a png to jpg</h1>

                <form action="/convert" method="post" enctype="multipart/form-data">
                    <input type="file" name="img_file" />
                    <input type="submit" />
                </form>
            </body>
        </html>
    """

@app.route('/convert', methods=["POST"])
def convert_view():
    file = request.files['img_file']
    if not file:
        return "No file"

    png = Image.open(file)

    result = transform(png)

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=result_image.jpg"
    return response


if __name__ == "__main__":
	app.run(port=5000, debug=True)