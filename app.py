from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def uploading():
    files = request.files.getlist('file')

    for file in files:
        if  file.filename != "":
            file.save('uploads/' + file.filename)

    return "Files uploaded successfully"

if __name__ == "__main__":
    app.run(debug=True)