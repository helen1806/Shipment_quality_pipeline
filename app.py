from flask import Flask, render_template, request, send_file, session
import os
import io
import pandas as pd

app = Flask(__name__)
app.secret_key = 'etl-secret-key'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


cleaned_store = {}


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def uploading():
    files = request.files.getlist('file')
    file_columns = {}

    for file in files:
        if file.filename != "":
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            df = pd.read_csv(path)
            file_columns[file.filename] = df.columns.tolist()
    

    return render_template(
        "index.html",
        column_section=True,
        file_columns=file_columns
    )


@app.route('/clean', methods=['POST'])
def clean():
    filename = request.form.get('filename')
    column = request.form.get('column')
    action = request.form.get('action')

    path = os.path.join(UPLOAD_FOLDER, filename)
    df = pd.read_csv(path)

    original_rows = len(df)

    if action == "remove_nulls":
        df = df.dropna(subset=[column])
        op_label = f"Removed nulls from <strong>{column}</strong>"
    elif action == "drop_duplicates":
        df = df.drop_duplicates(subset=[column])
        op_label = f"Dropped duplicates in <strong>{column}</strong>"
    elif action == "lowercase":
        df[column] = df[column].astype(str).str.lower()
        op_label = f"Lowercased <strong>{column}</strong>"
    elif action == "uppercase":
        df[column] = df[column].astype(str).str.upper()
        op_label = f"Uppercased <strong>{column}</strong>"
    elif action == "delete_column":
        df = df.drop(columns=[column])
        op_label = f"Deleted column <strong>{column}</strong>"
    else:
        op_label = "Unknown operation"

    new_rows = len(df)
    rows_affected = original_rows - new_rows


    cleaned_store[filename] = df

    table_html = df.to_html(classes='data-table', border=0, index=False)

    return render_template(
        "result.html",
        table=table_html,
        filename=filename,
        op_label=op_label,
        original_rows=original_rows,
        new_rows=new_rows,
        rows_affected=rows_affected,
        columns=len(df.columns)
    )


@app.route('/download/<filename>')
def download(filename):
    df = cleaned_store.get(filename)
    if df is None:
        return "File not found. Please re-apply the operation.", 404

    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    download_name = f"cleaned_{filename}"
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=download_name
    )

@app.route('/upload-to-db/<filename>')
def upload_to_db():
   
    return "Uploaded"


if __name__ == "__main__":
    app.run(debug=True)
