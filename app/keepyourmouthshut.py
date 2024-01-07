from flask import Flask, render_template, request, send_file
import os
import zipfile
from generate_podcast import generate_podcast

app = Flask(__name__)


@app.route("/")
def index():
    """
    Route handler for the root URL ("/").

    Returns:
        flask.Response: The response object containing the rendered "index.html" template.
    """
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    Route handler for generating a podcast based on user-submitted form data.

    This route expects a POST request with the following form parameters:
    - 'name': Name of the podcast.
    - 'desc': Description of the podcast.
    - 'topic1', 'topic2', 'topic3': Topics to be covered in the podcast.
    - 'advert1', 'advert2': Advertisements to be included in the podcast.

    The generated podcast includes the provided information and is packaged into a ZIP file
    containing both an MP3 audio file and a corresponding text transcript file.

    Returns:
        flask.Response: A response object containing the ZIP file for download.
    """
    name = request.form["name"]
    desc = request.form["desc"]
    topic1 = request.form["topic1"]
    topic2 = request.form["topic2"]
    topic3 = request.form["topic3"]
    advert1 = request.form["advert1"]
    advert2 = request.form["advert2"]

    topics = [topic1, topic2, topic3]
    adverts = [advert1, advert2]

    # Generate the podcast
    mp3_file, txt_file = generate_podcast(name, desc, topics, adverts)

    # Set the working directory to the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    # Use relative paths for the files, assuming the script is in the 'app' directory
    mp3_file = os.path.join(".", "downloads", mp3_file)
    txt_file = os.path.join(".", "downloads", txt_file)

    zip_folder = os.path.join(".", "downloads")
    zip_filename = f"{zip_folder}/{name}_podcast.zip"

    # Ensure the output directory exists
    os.makedirs(zip_folder, exist_ok=True)

    # Zip the two files
    with zipfile.ZipFile(zip_filename, "w") as zip_file:
        zip_file.write(mp3_file, arcname=os.path.basename(mp3_file))
        zip_file.write(txt_file, arcname=os.path.basename(txt_file))

    # Send the zip file to the user for download
    return send_file(f"./downloads/{name}_podcast.zip", as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=64215, debug=True)
