from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Rotifer WebApp</title>
    <style>
        body { font-family: Arial, sans-serif; }
        #drop-area {
            border: 2px dashed #ccc;
            border-radius: 20px;
            width: 80%;
            margin: auto;
            padding: 20px;
            text-align: center;
        }
        #results { margin-top: 20px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>Rotifer Interactive Webapp</h1>
    <div id="drop-area">
        <p>Drag & drop FASTA file here, or click to select.</p>
        <input type="file" id="fileElem" accept=".fa,.fasta" style="display:none">
        <button id="fileSelect">Select File</button>
    </div>
    <pre id="results"></pre>
<script>
var dropArea = document.getElementById('drop-area');

['dragenter','dragover','dragleave','drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults (e) {
  e.preventDefault();
  e.stopPropagation();
}

dropArea.addEventListener('drop', handleDrop, false);
document.getElementById('fileSelect').addEventListener('click', () => fileElem.click());
document.getElementById('fileElem').addEventListener('change', handleFiles, false);

function handleDrop(e) {
  var dt = e.dataTransfer;
  var files = dt.files;
  handleFiles({target:{files: files}});
}

function handleFiles(e) {
  var files = e.target.files;
  if(!files.length) return;
  var formData = new FormData();
  formData.append('file', files[0]);
  fetch('/analyze', {
    method: 'POST',
    body: formData
  })
  .then(r => r.json())
  .then(data => {
    document.getElementById('results').textContent = JSON.stringify(data, null, 2);
  })
}
</script>
</body>
</html>
'''

def gc_content(seq: str) -> float:
    seq = seq.upper()
    g = seq.count('G')
    c = seq.count('C')
    return round((g + c) / len(seq) * 100, 2) if len(seq) > 0 else 0.0

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    text = f.read().decode('utf-8')
    sequences = []
    current_id = None
    current_seq = []
    for line in text.splitlines():
        if line.startswith('>'):
            if current_id is not None:
                seq = ''.join(current_seq)
                sequences.append({'id': current_id,
                                   'length': len(seq),
                                   'gc_content': gc_content(seq)})
            current_id = line[1:].strip()
            current_seq = []
        else:
            current_seq.append(line.strip())
    if current_id is not None:
        seq = ''.join(current_seq)
        sequences.append({'id': current_id,
                           'length': len(seq),
                           'gc_content': gc_content(seq)})
    return jsonify(sequences)

if __name__ == '__main__':
    app.run(debug=True)
