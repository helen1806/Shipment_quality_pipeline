from flask import Flask, render_template, request, send_file, session
from  databaseConnection import insert_user_dataset
import os
import io
import pandas as pd
from flask import request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

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

@app.route('/store-user', methods=['POST'])
def store_user():
    data = request.get_json()
    session["user_id"] = data.get("user_id")
    
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


@app.route('/upload-to-db/<filename>', methods=['POST'])
def upload_to_db(filename):
    insert_user_dataset(filename)
    return "Dataset Uploaded"
    


@app.route('/editor')
def query():


    return render_template('editor.html')


@app.route('/run-query', methods=['POST'])
def run_query():
   
    conn = psycopg2.connect(os.environ.get("DB_URL"))
    cur = conn.cursor()

    try:
        cur.execute(query)

        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return jsonify({"rows": result})
        else:
            conn.commit()
            return jsonify({"message": "Query executed successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        cur.close()
        conn.close()


@app.route('/login',methods=['POST'])
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
