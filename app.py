
from flask import Flask, request, render_template_string, send_file
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>بشراك للهوية</title>
</head>
<body>
    <h2>ارفع صورتك لتجهيزها</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required>
        <button type="submit">معالجة الصورة</button>
    </form>
    {% if image_url %}
        <h3>الصورة جاهزة:</h3>
        <img src="{{ image_url }}" style="max-width:300px;">
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    if request.method == "POST":
        file = request.files["image"]
        img = Image.open(file.stream).convert("RGB")
        result = remove(img)
        output = io.BytesIO()
        result.save(output, format="JPEG", quality=85)
        output.seek(0)
        return send_file(output, mimetype="image/jpeg")
    return render_template_string(HTML_TEMPLATE, image_url=image_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
