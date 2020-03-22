#!/usr/bin/python3

from flask import Flask, request, send_from_directory, render_template

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='', template_folder='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/data/<path:path>')
def send_data(path):
    return send_from_directory('data', path)

@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('lib', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)

if __name__ == "__main__":
    app.run()

