from flask import Flask, session, redirect, url_for, request, render_template, send_file
import glob
import os

app = Flask(__name__)
app.debug = True
video_path = 'A:/su/cutresults/'
expansion = 'flv'
videos = glob.glob(video_path + "/*." + expansion)
videos_name = []
content = ''
name2path = {}
for v in videos:
    name = os.path.basename(v)
    filename, file_extension = os.path.splitext(name)
    content += '<li><a href="/%s">%s</a></li>' %(filename, filename)
    videos_name.append(filename)
    name2path[filename] = v.replace('\\', '/')

@app.route('/')
def index():
    return '<ol>' + content + '</ol>'

@app.route('/<name>')
def label_page(name=None):
    return render_template('index.html', name=name)

@app.route('/video/<name>')
def video_file_server(name=None):
    path = name2path[name]
    resp = send_file(path, mimetype='video/x-flv')

    return resp

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = '\xbd\xba\x1a\xa5\x047y\x94}E\xc9}\xa6\xda(\xa7\xa2`,\x8bzU\xda\x19'

if __name__ == '__main__':
    app.run()
