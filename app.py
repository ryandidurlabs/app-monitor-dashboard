import os
from flask import Flask, send_from_directory, abort


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "template")

# Serve static files directly from the existing `template` directory
app = Flask(
    __name__,
    static_folder="template",
    static_url_path="",
    template_folder="template",
)


@app.get("/health")
def health() -> str:
    return "ok"


@app.get("/")
def index():
    # Serve the main dashboard page
    return send_from_directory(TEMPLATE_DIR, "index.html")


@app.get("/<string:page>")
@app.get("/<string:page>.html")
def page_router(page: str):
    # Only allow single-segment pages, to avoid catching static assets
    filename = f"{page}.html"
    file_path = os.path.join(TEMPLATE_DIR, filename)
    if os.path.isfile(file_path):
        return send_from_directory(TEMPLATE_DIR, filename)
    abort(404)


@app.get("/pages")
def list_pages():
    # Simple sitemap of available top-level pages
    try:
        entries = []
        for name in sorted(os.listdir(TEMPLATE_DIR)):
            if not name.lower().endswith(".html"):
                continue
            if name.startswith("errors-"):
                continue
            entries.append(name)
        if not entries:
            return "No pages found", 200
        links = "".join(
            f"<li><a href='/{n[:-5]}'>{n}</a></li>" for n in entries
        )
        return f"<h1>Pages</h1><ul>{links}</ul>", 200
    except Exception:
        abort(500)


@app.errorhandler(404)
def not_found(_):
    # Try to serve themed 404 page if available
    custom_404 = os.path.join(TEMPLATE_DIR, "errors-404.html")
    if os.path.isfile(custom_404):
        return send_from_directory(TEMPLATE_DIR, "errors-404.html"), 404
    return "Not Found", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
