import os
from flask import Flask, render_template, request, send_file, url_for, redirect
from resemble import Resemble


app = Flask(__name__)


def _init_resemble():
    """
    Initialize Resemble SDK from environment variable.
    """
    api_key = os.getenv("RESEMBLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing RESEMBLE_API_KEY environment variable. Set it to your Resemble API key."
        )
    Resemble.api_key(api_key)


def _get_default_project_uuid():
    projects = Resemble.v2.projects.all(1, 10)
    items = projects.get("items", []) if isinstance(projects, dict) else []
    if not items:
        raise RuntimeError("No Resemble projects found in your account.")
    return items[0]["uuid"]


def _get_default_voice_uuid():
    voices = Resemble.v2.voices.all(1, 10)
    items = voices.get("items", []) if isinstance(voices, dict) else []
    if not items:
        raise RuntimeError("No Resemble voices found in your account.")
    return items[0]["uuid"]


OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "static", "output.wav")


@app.route("/", methods=["GET", "POST"])
def index():
    audio_url = None
    error = None
    if request.method == "POST":
        text = (request.form.get("text") or "").strip()
        if not text:
            error = "Please enter some text."
        else:
            try:
                _init_resemble()
                project_uuid = _get_default_project_uuid()
                voice_uuid = _get_default_voice_uuid()

                # Create a clip synchronously
                clip = Resemble.v2.clips.create_sync(
                    project_uuid,
                    voice_uuid,
                    text,
                    title=None,
                    sample_rate=44100,
                    output_format="wav",
                    precision=None,
                    include_timestamps=None,
                    is_archived=None,
                    raw=None,
                )

                audio_src = clip.get("audio_src") if isinstance(clip, dict) else None
                if not audio_src:
                    raise RuntimeError("Clip created but no audio_src was returned.")

                # Fetch binary audio and save as output.wav
                # The SDK returns a URL; we'll download the content.
                import urllib.request

                os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
                with urllib.request.urlopen(audio_src) as resp, open(OUTPUT_PATH, "wb") as f:
                    f.write(resp.read())

                audio_url = url_for("static", filename="output.wav")
            except Exception as e:
                error = str(e)

    return render_template("index.html", audio_file=audio_url, error=error)


@app.route("/download")
def download():
    if not os.path.exists(OUTPUT_PATH):
        return redirect(url_for("index"))
    return send_file(OUTPUT_PATH, as_attachment=True)


if __name__ == "__main__":
    # Optional: allow host/port overrides via env
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
