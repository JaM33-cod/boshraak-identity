from flask import Flask, request, render_template_string, send_file
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>بشراك للهوية</title>
    <style>
        body { font-family: Tahoma, sans-serif; text-align: center; padding: 20px; background-color: #f8f9fa; }
        h2 { color: #2c3e50; }
        form { margin-top: 20px; }
        button { padding: 10px 20px; background-color: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #219150; }
        img { margin-top: 20px; border: 2px solid #ddd; max-width: 320px; }
    </style>
</head>
<body>
    <h2>✦ بشراك للهوية ✦</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required>
        <button type="submit">معالجة الصورة</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        img = Image.open(file.stream).convert("RGB")

        # إزالة الخلفية
        result = remove(img)

        # تغيير الحجم إلى 640x480
        result = result.resize((640, 480))

        # حفظ الصورة بجودة مناسبة وحجم أقل من 1MB
        output = io.BytesIO()
        result.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)

        return send_file(output, mimetype="image/jpeg")

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
