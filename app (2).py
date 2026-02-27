from flask import Flask, request, render_template_string
import time
from auto_brain_core import process_video

app = Flask(__name__)

MAX_LINKS_PER_RUN = 6
SLEEP_BETWEEN_LINKS = 1.5

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Auto TikTok Comment Likes</title>
  <style>
    body{font-family:system-ui;background:#0b1220;color:#e5e7eb;display:flex;justify-content:center;padding:24px}
    .card{width:100%;max-width:900px;background:#0f172a;border:1px solid #334155;border-radius:16px;padding:18px}
    textarea{width:100%;min-height:220px;background:#0b1220;color:#e5e7eb;border:1px solid #334155;border-radius:12px;padding:12px}
    button{margin-top:10px;padding:10px 16px;border-radius:999px;border:none;background:#6366f1;color:white;font-weight:700;cursor:pointer}
    pre{white-space:pre-wrap;background:#0b1220;border:1px solid #334155;border-radius:12px;padding:12px;margin-top:14px}
  </style>
</head>
<body>
  <div class="card">
    <h2>Encrypted Money Code Likes Bot</h2>
    <p>Paste TikTok video links (1 per line):</p>
    <form method="post">
      <textarea name="links">{{links}}</textarea>
      <button type="submit">🚀 Run</button>
    </form>
    {% if log %}
      <pre>{{log}}</pre>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    links_text = ""
    logs = []

    if request.method == "POST":
        links_text = request.form.get("links","")
        raw_links = [l.strip() for l in links_text.splitlines() if l.strip()]

        if len(raw_links) > MAX_LINKS_PER_RUN:
            raw_links = raw_links[:MAX_LINKS_PER_RUN]
            logs.append(f"[INFO] Limit {MAX_LINKS_PER_RUN} links per run.")

        for idx, url in enumerate(raw_links, start=1):
            res = process_video(url)
            logs.append(f"{idx}) {url} -> {res}")
            time.sleep(SLEEP_BETWEEN_LINKS)

    return render_template_string(HTML, links=links_text, log="\n".join(logs))

if __name__ == "__main__":
    app.run(debug=True)
