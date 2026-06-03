from flask import Flask, render_template, request, jsonify, send_file
from ranker import rank_resumes
import os, csv, io

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rank", methods=["POST"])
def rank():
    job_desc = request.form.get("job_description", "")
    files = request.files.getlist("resumes")

    if not job_desc or not files:
        return jsonify({"error": "Missing input"}), 400

    saved_paths = []
    for f in files:
        if f.filename.endswith(".pdf"):
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            saved_paths.append(path)

    results = rank_resumes(job_desc, saved_paths)
    return jsonify({"results": results})

@app.route("/download", methods=["POST"])
def download():
    data = request.json.get("results", [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Resume", "Score (%)"])
    for i, (name, score) in enumerate(data, 1):
        writer.writerow([i, name, score])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="hr_report.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)