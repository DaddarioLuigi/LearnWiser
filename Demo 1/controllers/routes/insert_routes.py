from flask import Blueprint, render_template, request, redirect,url_for
import os

insert = Blueprint('insert', __name__)

@insert.route('/', methods=['GET','POST'])
def insert_document():
    if request.method == 'POST':
        # Get the uploaded file
        doc = request.files.get("fileUpload")

        if doc:
           # Specify absolute path for saving
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)  # Create directory if not exists
            doc.save(os.path.join(upload_folder, doc.filename))
            return redirect(url_for('quiz.insert_answer'))

    return render_template("home.html")

