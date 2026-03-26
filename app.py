from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from databaseConnection import insert_user_dataset, get_uploaded_tables
import os
import io
import json
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET", "etl-secret-key")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024

datasets = {}


def compute_profile(df):
    profile = []
    total_rows = len(df)
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        unique_count = int(df[col].nunique())
        dtype = str(df[col].dtype)
        null_pct = round((null_count / total_rows * 100), 1) if total_rows > 0 else 0
        profile.append({
            "column": col,
            "dtype": dtype,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count
        })
    return profile


def compute_quality_score(df):
    total_rows = len(df)
    if total_rows == 0:
        return 0
    total_cells = total_rows * len(df.columns)
    null_cells = int(df.isnull().sum().sum())
    dup_rows = int(df.duplicated().sum())
    null_score = max(0, 100 - (null_cells / total_cells * 100)) if total_cells > 0 else 100
    dup_score = max(0, 100 - (dup_rows / total_rows * 100)) if total_rows > 0 else 100
    return round((null_score * 0.6 + dup_score * 0.4), 1)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    files = request.files.getlist("file")
    results = []

    for file in files:
        if not file.filename:
            continue

        if not file.filename.lower().endswith(".csv"):
            results.append({"filename": file.filename, "error": "Only CSV files are supported"})
            continue

        content = file.read()
        if len(content) > MAX_FILE_SIZE:
            results.append({"filename": file.filename, "error": "File exceeds 50MB limit"})
            continue

        if len(content) == 0:
            results.append({"filename": file.filename, "error": "File is empty"})
            continue

        try:
            df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(io.BytesIO(content), encoding="latin-1")
            except Exception as e:
                results.append({"filename": file.filename, "error": f"Could not parse CSV: {str(e)}"})
                continue
        except Exception as e:
            results.append({"filename": file.filename, "error": f"Invalid CSV: {str(e)}"})
            continue

        if df.empty or len(df.columns) == 0:
            results.append({"filename": file.filename, "error": "CSV has no data or columns"})
            continue

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(path, "wb") as f:
            f.write(content)

        datasets[file.filename] = {
            "original": df.copy(),
            "working": df.copy(),
            "history": []
        }

        preview = df.head(20).fillna("").to_dict(orient="records")
        profile = compute_profile(df)
        quality = compute_quality_score(df)

        results.append({
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": preview,
            "profile": profile,
            "quality_score": quality
        })

    return jsonify({"results": results})


@app.route("/api/datasets", methods=["GET"])
def list_datasets():
    result = []
    for name, data in datasets.items():
        df = data["working"]
        result.append({
            "filename": name,
            "rows": len(df),
            "columns": list(df.columns),
            "history_count": len(data["history"])
        })
    return jsonify({"datasets": result})


@app.route("/api/dataset/<filename>", methods=["GET"])
def get_dataset(filename):
    if filename not in datasets:
        return jsonify({"error": "Dataset not found"}), 404

    data = datasets[filename]
    df = data["working"]
    preview = df.head(20).fillna("").to_dict(orient="records")
    profile = compute_profile(df)
    quality = compute_quality_score(df)

    return jsonify({
        "filename": filename,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": preview,
        "profile": profile,
        "quality_score": quality,
        "history": data["history"]
    })


@app.route("/api/transform", methods=["POST"])
def transform():
    body = request.get_json()
    filename = body.get("filename")
    column = body.get("column")
    action = body.get("action")

    if filename not in datasets:
        return jsonify({"error": "Dataset not found"}), 404

    data = datasets[filename]
    df = data["working"].copy()
    original_rows = len(df)

    op_labels = {
        "remove_nulls": f"Remove nulls from '{column}'",
        "drop_duplicates": f"Drop duplicates in '{column}'",
        "lowercase": f"Lowercase '{column}'",
        "uppercase": f"Uppercase '{column}'",
        "trim": f"Trim whitespace in '{column}'",
        "delete_column": f"Delete column '{column}'",
        "fill_nulls_mean": f"Fill nulls with mean in '{column}'",
        "fill_nulls_mode": f"Fill nulls with mode in '{column}'",
        "fill_nulls_empty": f"Fill nulls with empty string in '{column}'"
    }

    if action not in op_labels:
        return jsonify({"error": "Unknown operation"}), 400

    if action != "drop_duplicates" and column not in df.columns and action != "drop_duplicates":
        if action not in ["drop_duplicates"] and column not in df.columns:
            return jsonify({"error": f"Column '{column}' not found"}), 400

    try:
        if action == "remove_nulls":
            df = df.dropna(subset=[column])
        elif action == "drop_duplicates":
            df = df.drop_duplicates(subset=[column] if column else None)
        elif action == "lowercase":
            df[column] = df[column].astype(str).str.lower()
        elif action == "uppercase":
            df[column] = df[column].astype(str).str.upper()
        elif action == "trim":
            df[column] = df[column].astype(str).str.strip()
        elif action == "delete_column":
            df = df.drop(columns=[column])
        elif action == "fill_nulls_mean":
            df[column] = df[column].fillna(df[column].mean())
        elif action == "fill_nulls_mode":
            df[column] = df[column].fillna(df[column].mode()[0] if not df[column].mode().empty else "")
        elif action == "fill_nulls_empty":
            df[column] = df[column].fillna("")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    new_rows = len(df)
    rows_affected = original_rows - new_rows

    step = {
        "step": len(data["history"]) + 1,
        "action": action,
        "column": column,
        "label": op_labels[action],
        "rows_before": original_rows,
        "rows_after": new_rows,
        "rows_affected": rows_affected
    }

    data["working"] = df
    data["history"].append(step)

    path = os.path.join(UPLOAD_FOLDER, filename)
    df.to_csv(path, index=False)

    preview = df.head(20).fillna("").to_dict(orient="records")
    profile = compute_profile(df)
    quality = compute_quality_score(df)

    return jsonify({
        "filename": filename,
        "rows": new_rows,
        "columns": list(df.columns),
        "rows_affected": rows_affected,
        "preview": preview,
        "profile": profile,
        "quality_score": quality,
        "history": data["history"],
        "step": step
    })


@app.route("/api/reset/<filename>", methods=["POST"])
def reset_dataset(filename):
    if filename not in datasets:
        return jsonify({"error": "Dataset not found"}), 404

    data = datasets[filename]
    data["working"] = data["original"].copy()
    data["history"] = []

    path = os.path.join(UPLOAD_FOLDER, filename)
    data["original"].to_csv(path, index=False)

    df = data["working"]
    preview = df.head(20).fillna("").to_dict(orient="records")
    profile = compute_profile(df)
    quality = compute_quality_score(df)

    return jsonify({
        "filename": filename,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": preview,
        "profile": profile,
        "quality_score": quality,
        "history": []
    })


@app.route("/api/delete/<filename>", methods=["DELETE"])
def delete_dataset(filename):
    if filename not in datasets:
        return jsonify({"error": "Dataset not found"}), 404

    del datasets[filename]
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)

    return jsonify({"success": True})


@app.route("/api/download/<filename>")
def download(filename):
    fmt = request.args.get("format", "csv")

    if filename not in datasets:
        return jsonify({"error": "Dataset not found"}), 404

    df = datasets[filename]["working"]

    if fmt == "json":
        buffer = io.BytesIO()
        buffer.write(df.to_json(orient="records", indent=2).encode("utf-8"))
        buffer.seek(0)
        return send_file(buffer, mimetype="application/json", as_attachment=True,
                         download_name=f"cleaned_{filename.replace('.csv', '.json')}")
    else:
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype="text/csv", as_attachment=True,
                         download_name=f"cleaned_{filename}")


@app.route("/api/load-to-db/<filename>", methods=["POST"])
def load_to_db(filename):
    if filename not in datasets:
        return jsonify({"error": "Dataset not found"}), 404

    df = datasets[filename]["working"]

    path = os.path.join(UPLOAD_FOLDER, filename)
    df.to_csv(path, index=False)

    try:
        result = insert_user_dataset(filename, df)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/run-query", methods=["POST"])
def run_query():
    body = request.get_json()
    query = body.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    db_url = os.environ.get("DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        return jsonify({"error": "No database connection configured"}), 500

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    try:
        cur.execute(query)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return jsonify({"columns": columns, "rows": result, "row_count": len(result)})
        else:
            conn.commit()
            return jsonify({"message": "Query executed successfully", "rows": [], "columns": []})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()


@app.route("/api/tables", methods=["GET"])
def get_tables():
    try:
        tables = get_uploaded_tables()
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"tables": [], "error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
