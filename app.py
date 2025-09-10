from flask import Flask, request, jsonify, send_file
import os, uuid
from TTS.api import TTS

app = Flask(__name__)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



@app.route("/clone", methods=["POST"])
def clone():
    """
    POST /clone
    form-data:
      - sample (file: wav/mp3/flac)
      - text (string)
    returns: generated wav file
    """
    if "sample" not in request.files or "text" not in request.form:
        return jsonify({"error": "sample (file) and text (str) required"}), 400
    
    sample = request.files["sample"]
    text = request.form["text"].strip()
    if not text:
        return jsonify({"error": "Text cannot be empty"}), 400

    # save input file
    uid = uuid.uuid4().hex[:8]
    in_path = os.path.join(UPLOAD_DIR, f"{uid}.wav")
    sample.save(in_path)

    # run TTS with voice conversion
    out_path = os.path.join(OUTPUT_DIR, f"{uid}_out.wav")
    try:
        tts.tts_with_vc_to_file(text=text, speaker_wav=in_path, file_path=out_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # send back file
    return send_file(out_path, as_attachment=True, download_name="cloned.wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
