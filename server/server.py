from flask import Flask, request, jsonify, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# الإعدادات
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATA_FILE = os.path.join(BASE_DIR, "data.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# تحميل البيانات
# =========================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "products": [],
        "sections": {
            "حلويات": [],
            "عصائر": [],
            "إجباس": []
        }
    }

# =========================
# الصفحة الرئيسية
# =========================
@app.route("/")
def index():
    return "Server is running"

# =========================
# جلب كل المنتجات
# =========================
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(data)

# =========================
# إضافة منتج (للأدمن)
# =========================
@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")

        if not name or not price or not category:
            return jsonify({"error": "بيانات ناقصة"}), 400

        if "image" not in request.files:
            return jsonify({"error": "الصورة غير موجودة"}), 400

        image = request.files["image"]
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

        product = {
            "name": name,
            "price": price,
            "category": category,
            "image": f"/uploads/{filename}"
        }

        data["products"].append(product)

        if category not in data["sections"]:
            data["sections"][category] = []

        data["sections"][category].append(product)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return jsonify({"message": "تمت إضافة المنتج", "product": product})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# عرض الصور
# =========================
@app.route("/uploads/<filename>")
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# =========================
# تشغيل محلي فقط
# =========================
if __name__ == "__main__":
    app.run(debug=True)
