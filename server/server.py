from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, cgi

DATA_FILE = "data.json"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"products": []}, f, ensure_ascii=False, indent=2)

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/products":
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/add":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"}
            )

            name = form.getvalue("name")
            price = form.getvalue("price")
            category = form.getvalue("category")
            image = form["image"] if "image" in form else None

            if not name or not price or not category or not image:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("بيانات ناقصة".encode("utf-8"))
                return

            filename = str(int(os.times()[4]*1000)) + "_" + image.filename
            with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
                f.write(image.file.read())

            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["products"].append({
                "name": name,
                "price": price,
                "category": category,
                "image": filename
            })

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.end_headers()
            self.wfile.write("تمت إضافة المنتج".encode("utf-8"))

server = HTTPServer(("0.0.0.0", 8000), Handler)
print("Server running on http://localhost:8000")
server.serve_forever()
