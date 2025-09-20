from flask import Flask, request, render_template_string, send_from_directory
import socket
import os
import qrcode

app = Flask(__name__)

# Folder where files will be stored
UPLOAD_FOLDER = "shared_files"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_local_ip():
    """Find local IP (works for WiFi, LAN, Hotspot)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        f = request.files["file"]
        if f.filename == "":
            return "Empty filename", 400
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        return f"<p>✅ Uploaded: {f.filename}</p><a href='/'>Back</a>"

    files = os.listdir(UPLOAD_FOLDER)
    files_list = "".join(
        [f"<li><a href='/download/{file}'>{file}</a></li>" for file in files]
    )

    return render_template_string("""
        <h2>📂 File Sharing</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>
        <h3>Available Files:</h3>
        <ul>{{ files|safe }}</ul>
    """, files=files_list)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    ip = get_local_ip()
    url = f"http://{ip}:5000"

    print(f"\nShare this link: {url}")
    print("Or scan this QR code:\n")

    # Print QR code in terminal
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr.print_ascii(invert=True)

    app.run(host="0.0.0.0", port=5000, debug=False)
