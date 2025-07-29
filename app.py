from flask import Flask, render_template_string, request, send_file
from rembg import remove
from PIL import Image, ImageOps
import io
import numpy as np
import cv2

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>بشراك للهوية</title>
    <style>
        body { font-family: Tahoma, Arial; text-align: center; background-color: #f9f9f9; direction: rtl; }
        h1 { color: #006c35; }
        form { margin: 30px; padding: 20px; border: 2px dashed #006c35; background: white; display: inline-block; }
        input[type=file], input[type=submit] {
            margin: 10px; padding: 10px; font-size: 16px;
        }
        img { margin-top: 20px; border: 3px solid #006c35; max-width: 90%; }
    </style>
</head>
<body>
    <h1>📸 بشراك للهوية</h1>
    <p>حمّل صورتك وسيتم تجهيزها بالمواصفات الرسمية</p>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required>
        <br>
        <input type="submit" value="تجهيز الصورة">
    </form>
    {% if processed %}
        <h2>✅ صورتك جاهزة للهوية</h2>
        <img src="data:image/jpeg;base64,{{ processed }}" alt="الصورة الجاهزة">
        <br><br>
        <a href="/download">⬇️ تحميل الصورة</a>
    {% endif %}
</body>
</html>"""

processed_image_bytes = None

@app.route("/", methods=["GET", "POST"])
def index():
    global processed_image_bytes
    if request.method == "POST":
        file = request.files["image"]
        img = Image.open(file.stream).convert("RGB")

        # إزالة الخلفية
        arr = np.array(img)
        img_no_bg = remove(arr)

        # إضافة خلفية بيضاء
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        rgba_img = Image.fromarray(img_no_bg)
        img_white = Image.composite(rgba_img, white_bg, rgba_img.split()[3])

        # كشف الوجه وتوسيطه
        np_img = np.array(img_white)
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) > 0:
            x, y, w, h = faces[0]
            pad_x, pad_y = int(w*0.6), int(h*1.5)
            crop_img = np_img[max(0,y-pad_y):y+h+pad_y, max(0,x-pad_x):x+w+pad_x]
            img_white = Image.fromarray(crop_img)

        # تغيير المقاس إلى 640x480
        img_final = ImageOps.fit(img_white, (640, 480), Image.LANCZOS)

        # حفظ بجودة تقلل الحجم
        buf = io.BytesIO()
        img_final.save(buf, format="JPEG", quality=85, optimize=True)
        processed_image_bytes = buf.getvalue()

        import base64
        processed_b64 = base64.b64encode(processed_image_bytes).decode("utf-8")

        return render_template_string(HTML_PAGE, processed=processed_b64)

    return render_template_string(HTML_PAGE, processed=None)

@app.route("/download")
def download():
    return send_file(
        io.BytesIO(processed_image_bytes),
        mimetype="image/jpeg",
        as_attachment=True,
        download_name="boshraak_identity.jpg"
    )

if __name__ == "__main__":
    app.run()
