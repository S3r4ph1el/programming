import os
import tempfile
import subprocess
import shutil
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, send_file

app = Flask(__name__)
app.secret_key = '7e052f614c5f9d5da3249cc4c6d9a950053aed370b8464d2e8a81d41ff0e3371'

UPLOAD_FOLDER = '/tmp/variabype_uploads'
DOWNLOAD_FOLDER = '/var/www/portal.variatype.htb/public/files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/tools/variable-font-generator')
def variable_font_generator():
    return render_template('tools/variable_font_generator.html')

@app.route('/tools/variable-font-generator/process', methods=['POST'])
def process_variable_font():
    designspace = request.files.get('designspace')
    master_fonts = request.files.getlist('masters')

    if not designspace or not master_fonts:
        flash('Please upload a .designspace file and at least one master font (.ttf/.otf).', 'error')
        return redirect(url_for('variable_font_generator'))

    if not designspace.filename.endswith('.designspace'):
        flash('The main file must be a valid .designspace document.', 'error')
        return redirect(url_for('variable_font_generator'))

    unique_id = secrets.token_urlsafe(8)
    download_filename = f"variabype_{unique_id}.ttf"
    download_path = os.path.join(DOWNLOAD_FOLDER, download_filename)

    with tempfile.TemporaryDirectory(dir=UPLOAD_FOLDER) as workdir:
        ds_path = os.path.join(workdir, 'config.designspace')
        designspace.save(ds_path)

        for font in master_fonts:
            if font.filename.endswith(('.ttf', '.otf')):
                font.save(os.path.join(workdir, font.filename))
            else:
                flash('Only .ttf and .otf master fonts are supported.', 'error')
                return redirect(url_for('variable_font_generator'))

        try:
            subprocess.run(
                ['fonttools', 'varLib', 'config.designspace'],
                cwd=workdir,
                check=True,
                timeout=30
            )

            output_file = None
            for f in os.listdir(workdir):
                if f != 'config.designspace' and not f.startswith('.'):
                    output_file = f
                    break

            if output_file:
                shutil.copy2(os.path.join(workdir, output_file), download_path)

            return render_template('tools/success.html', download_id=unique_id)

        except subprocess.TimeoutExpired:
            flash('Font generation timed out.', 'error')
            return redirect(url_for('variable_font_generator'))
        except subprocess.CalledProcessError:
            flash('Font generation failed during processing.', 'error')
            return redirect(url_for('variable_font_generator'))
        except Exception:
            flash('An unexpected error occurred.', 'error')
            return redirect(url_for('variable_font_generator'))

@app.route('/download/<download_id>')
def download_file(download_id):
    if not download_id.replace('_', '').replace('-', '').isalnum():
        flash('Invalid download ID.', 'error')
        return redirect(url_for('variable_font_generator'))

    filename = f"variabype_{download_id}.ttf"
    path = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(path):
        user_filename = f"MyVariableFont_{download_id}.ttf"
        return send_file(path, as_attachment=True, download_name=user_filename)
    else:
        flash('File not available for download.', 'error')
        return redirect(url_for('variable_font_generator'))
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
