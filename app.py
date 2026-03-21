from flask import Flask, render_template, request
import os
app = Flask(__name__)
import pandas as pd

@app.route('/')
def home():
    return render_template("index.html")
    
@app.route('/upload', methods=['POST'])
def uploading():
    files = request.files.getlist('file')
    file_columns = {}

    for file in files:
        if file.filename != "":
            path = os.path.join('uploads', file.filename)
            file.save(path)

            df = pd.read_csv(path)
            file_columns[file.filename] = df.columns.tolist()

    return render_template(
        "index.html",
        column_section=True,
        file_columns=file_columns
    )
    

    
    
    
if __name__ == "__main__":
    app.run(debug=True)