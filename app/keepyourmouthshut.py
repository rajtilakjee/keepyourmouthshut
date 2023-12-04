from flask import Flask, render_template, request, send_file
import os
import shutil
from generate_podcast import generate_podcast

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
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
    generate_podcast(name, desc, topics, adverts)

    # Create a zip file
    zip_filename = f"{name}_podcast.zip"
    zip_folder = "app/downloads/"
    shutil.make_archive(os.path.join(zip_folder, name), "zip", zip_folder)

    return send_file(zip_filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
