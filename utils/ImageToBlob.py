from flask import send_file
from io import StringIO, BytesIO

# convert a png to blob data
def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'png', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='blob')
