from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)
video_path = 'A:/su/cutresults/'

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

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