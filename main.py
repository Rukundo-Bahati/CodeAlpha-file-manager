from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
import os
import shutil
import os

app = Flask(__name__)

# Directory to store uploaded and processed files
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clean")
def clean_data():
   return render_template("cleanData.html")

@app.route('/organise', methods=['GET', 'POST'])
def organise():
    message = ""
    if request.method == 'POST':
        path = request.form.get('path')
        print(f"Received path: {path}")

        # Normalize the path to handle backslashes correctly
        path = path.replace("/", "\\")  # Optionally replace backslashes with slashes

        if not path:
            message = "Please provide a valid directory path."
            return render_template("organiser.html", message=message)

        # Check if the path exists
        if not os.path.exists(path):
            message = f"The directory '{path}' does not exist."
            return render_template("organiser.html", message=message)

        try:
            files = os.listdir(path)
            if not files:
                message = "The directory is empty."
            else:
                for file in files:
                    filename, extension = os.path.splitext(file)
                    extension = extension[1:]

                    # Create a subdirectory for the file type if it doesn't exist
                    target_dir = os.path.join(path, extension)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)

                    shutil.move(os.path.join(path, file), os.path.join(target_dir, file))

                message = "Files organized successfully!"
        except Exception as e:
            message = f"An error occurred: {str(e)}"

    return render_template("organiser.html", message=message)

# Route for file upload and data cleaning
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Load CSV data into DataFrame
        df = pd.read_csv(file_path)

        # Remove leading/trailing spaces and standardize text case
        df = df.apply(lambda x: x.str.strip().str.lower() if x.dtype == "object" else x)

        # Clean data (remove missing values and duplicates)
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        cleaned_file_path = os.path.join(PROCESSED_FOLDER, 'cleaned_' + file.filename)
        df.to_csv(cleaned_file_path, index=False)

        return send_file(cleaned_file_path, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
