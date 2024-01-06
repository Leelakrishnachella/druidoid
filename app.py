from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import cv2
from PIL import Image
import numpy as np
import pytesseract

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path, area_coords):
    img = cv2.imread(image_path)

    x, y, w, h = area_coords

    print("Original image dimensions:", img.shape)

    # Check if the cropped area is within the image bounds
    if x >= 0 and y >= 0 and x + w <= img.shape[1] and y + h <= img.shape[0]:
        # Crop the image based on the marked area
        cropped_img = img[y:y+h, x:x+w]

        print("Cropped image dimensions:", cropped_img.shape)

        if cropped_img.size > 0:  # Check if the cropped image is not empty
            # Save the cropped image to a temporary file (required for Tesseract)
            temp_file_path = 'temp_cropped_image.png'
            cv2.imwrite(temp_file_path, cropped_img)

            # Perform OCR using Tesseract
            text = pytesseract.image_to_string(Image.open(temp_file_path))

            # Remove temporary file
            os.remove(temp_file_path)

            return text
        else:
            print("Error: Cropped image is empty")
            return "Error: Cropped image is empty"
    else:
        print("Error: Invalid area coordinates")
        return "Error: Invalid area coordinates"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Get the marked area coordinates
            x = int(request.form['x']) if request.form['x'] else 0
            y = int(request.form['y']) if request.form['y'] else 0
            w = int(request.form['width']) if request.form['width'] else 0
            h = int(request.form['height']) if request.form['height'] else 0
            area_coords = (x, y, w, h)

            # Process the image
            result = process_image(file_path, area_coords)

            return render_template('result.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
