import os
from flask import Flask, request, render_template, send_file
import fitz  # PyMuPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def paraphrase_text(text):
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Paraphrase this text in a human style that doesn't look AI-generated."},
            {"role": "user", "content": text}
        ],
        temperature=0.7
    )
    return resp['choices'][0]['message']['content']

def save_as_pdf(text, out_path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(out_path)
    doc.build([Paragraph(text, styles["Normal"])])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    aggregated = ""
    uploaded = request.files.get('file')
    if uploaded:
        os.makedirs("uploads", exist_ok=True)
        p = os.path.join("uploads", uploaded.filename)
        uploaded.save(p)
        if uploaded.filename.lower().endswith('.pdf'):
            aggregated += extract_text_from_pdf(p)
    txt = request.form.get('text_input')
    if txt:
        aggregated += "\n" + txt
    result = paraphrase_text(aggregated)
    os.makedirs("completed", exist_ok=True)
    out = os.path.join("completed", "homework_result.pdf")
    save_as_pdf(result, out)
    return send_file(out, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
