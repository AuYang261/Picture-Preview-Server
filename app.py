from flask import Flask, render_template
import os
from PIL import Image
from config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)

# set the static folder to the current dir
app.static_folder = "static"
picture_path = app.config.get("PICTURE_PATH", ".")


def get_files(path1, path2=""):
    path = os.path.join(path1, path2)
    files = os.listdir(path)
    ret = []
    for f in files:
        if os.path.isdir(os.path.join(path, f)):
            ret.extend(get_files(path, f))
        else:
            ret.append(path2 + "/" + f)
    return ret


@app.route("/")
def index():
    # list all pictures in the current dir recursively
    pictures = get_files(picture_path)
    pictures = [f for f in pictures if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    return render_template(
        "/index.html",
        images=pictures,
    )


@app.route("/preview/<path:filename>")
def preview(filename):
    if not os.path.exists(
        os.path.join(app.static_folder, r"preview", os.path.basename(filename))
    ):
        os.makedirs(
            os.path.join(app.static_folder, r"preview", os.path.dirname(filename)),
            exist_ok=True,
        )
    if not os.path.exists(os.path.join(app.static_folder, r"preview", filename)):
        # generate the preview image
        img = Image.open(os.path.join(picture_path, filename))
        img.thumbnail((720, 720))
        img.save(os.path.join(app.static_folder, r"preview", filename))
    with open(os.path.join(app.static_folder, r"preview", filename), "rb") as f:
        return f.read()


@app.route("/view/<path:filename>")
def view(filename):
    pictures = get_files(picture_path)
    pictures = [f for f in pictures if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    i = pictures.index(filename)
    if i == len(pictures) - 1:
        i = 0
    else:
        i += 1
    return render_template(
        "/view.html",
        image=filename,
        next_image=pictures[i],
        prev_image=pictures[i - 2],
    )


@app.route("/file/<path:filename>")
def get_file(filename):
    path = os.path.join(picture_path, filename)
    with open(path, "rb") as f:
        return f.read()


@app.route("/static/<path:filename>")
def static_file(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(
        port=app.config.get("PROT", 80),
        host=app.config.get("HOST", "0.0.0.0"),
        debug=app.config.get("DEBUG", True),
    )
