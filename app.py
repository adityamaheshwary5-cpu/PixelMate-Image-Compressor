
from flask import Flask, render_template, request
from PIL import Image, UnidentifiedImageError
import os

from svd_compressor import compress_image

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Check allowed file extensions
def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in {"jpg", "jpeg", "png"}
    )


# Homepage
@app.route("/")
def home():

    return render_template("index.html")


# Image compression
@app.route("/compress", methods=["POST"])
def compress():

    if "image" not in request.files:

        return render_template(
            "index.html",
            message="Error: Please select an image."
        )

    file = request.files["image"]

    if file.filename == "":

        return render_template(
            "index.html",
            message="Error: No image selected."
        )

    if not allowed_file(file.filename):

        return render_template(
            "index.html",
            message="Error: Only JPG, JPEG and PNG files are allowed."
        )

    # Validate rank
    try:

        k = int(request.form.get("rank", ""))

        if k < 1:
            raise ValueError

    except (ValueError, TypeError):

        return render_template(
            "index.html",
            message="Error: Please enter a valid compression rank."
        )

    input_path = os.path.join(
        UPLOAD_FOLDER,
        "original.png"
    )

    output_path = os.path.join(
        UPLOAD_FOLDER,
        "compressed.png"
    )

    try:

        # Save uploaded image
        file.save(input_path)

        # Verify that it is a genuine image
        with Image.open(input_path) as uploaded_image:

            if uploaded_image.format not in ("JPEG", "PNG"):

                raise ValueError(
                    "Only JPG, JPEG and PNG images are supported."
                )

            uploaded_image.verify()

        # Perform SVD compression
        results = compress_image(
            input_path,
            output_path,
            k
        )

        # Send images and results to website
        return render_template(
            "index.html",
            original_image="uploads/original.png",
            compressed_image="uploads/compressed.png",
            quality_graph="uploads/quality_graph.png",
            message="Image compressed successfully!",
            results=results
        )

    except (UnidentifiedImageError, OSError):

        return render_template(
            "index.html",
            message="Error: The uploaded image is damaged or invalid."
        )

    except ValueError as error:

        return render_template(
            "index.html",
            message="Error: " + str(error)
        )

    except Exception as error:

        return render_template(
            "index.html",
            message="Error: Something went wrong. " + str(error)
        )


# Handle files larger than 10 MB
@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "index.html",
        message="Error: Image size must be less than 10 MB."
    ), 413


if __name__ == "__main__":

    app.run(debug=True)
