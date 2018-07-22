from flask import Flask, session, redirect, url_for, request, render_template, send_file, g, flash
import glob
import os
import sqlite3

# app.config
DATABASE = 'data.db'
DEBUG = True
SECRET_KEY = '\xbd\xba\x1a\xa5\x047y\x94}E\xc9}\xa6\xda(\xa7\xa2`,\x8bzU\xda\x19'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)

# windows
# mac
video_path = u'F:/视频/视频标注测试集'
expansion = 'flv'
videos = glob.glob(video_path + "/*." + expansion)  # 获得所有视频的绝对路径名
videos_name = []
name2path = {}  # 视频名:路径
for v in videos:
    name = os.path.basename(v)
    filename, file_extension = os.path.splitext(name)
    videos_name.append(filename)
    name2path[filename] = v.replace('\\', '/')


# 数据库连接
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Open a new database connection if there is none yet for the
        current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# search sqlite(video_name need expansion)
def search_data(video_path, video_name):
    radio_dict = {}
    cursor = g.db.execute("select arousal_level,excitement_level,pleasure_level,contentment_level,sleepiness_level,"
                          "depression_level,misery_level,distress_level from label_set where video_path='%s' and "
                          "video_name='%s'" % (video_path, video_name))

    for row in cursor:
        radio_dict['arousal_level'] = row[0]
        radio_dict['excitement_level'] = row[1]
        radio_dict['pleasure_level'] = row[2]
        radio_dict['contentment_level'] = row[3]
        radio_dict['sleepiness_level'] = row[4]
        radio_dict['depression_level'] = row[5]
        radio_dict['misery_level'] = row[6]
        radio_dict['distress_level'] = row[7]

    return radio_dict


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# 只执行一次这个函数(use python shell,carry out once)
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def connection():
    g.db = get_db()


@app.route('/')
def index():
    return render_template('login.html', error=None)


@app.route('/<name>')
def label_page(name=None):
    # 取出传递的request参数
    video_list_index = 0
    video_list_length = 0
    if request.args.get('video_list_index') is not None:
        video_list_index = int(request.args.get('video_list_index'))
    elif session.get('video_list_index') is not None:
        video_list_index = session.get('video_list_index')
        session.pop('video_list_index')
    if request.args.get('video_list_length') is not None:
        video_list_length = int(request.args.get('video_list_length'))
    elif session.get('video_list_length') is not None:
        video_list_length = session.get('video_list_length')
        session.pop('video_list_length')
    # 扩展:如果此视频已经被标注,先获取相应的值,预设radio
    radio_dict = search_data(video_path, name+'.'+expansion)
    if len(radio_dict) == 0:
        radio_dict = {'arousal_level': 0, 'excitement_level': 0, 'pleasure_level': 0,
                      'contentment_level': 0, 'sleepiness_level': 0, 'depression_level': 0,
                      'misery_level': 0, 'distress_level': 0}
    return render_template('index.html', name=name, arousal_level=radio_dict['arousal_level'],
                           excitement_level=radio_dict['excitement_level'],
                           pleasure_level=radio_dict['pleasure_level'],
                           contentment_level=radio_dict['contentment_level'],
                           sleepiness_level=radio_dict['sleepiness_level'],
                           depression_level=radio_dict['depression_level'],
                           misery_level=radio_dict['misery_level'],
                           distress_level=radio_dict['distress_level'],
                           video_list_index=video_list_index,
                           video_list_length=video_list_length)


@app.route('/prev/<video_list_index>/<video_list_length>')
def prev_video(video_list_index, video_list_length):
    i = int(video_list_index)-1
    session['video_list_index'] = i
    session['video_list_length'] = int(video_list_length)
    return redirect(url_for('label_page', name=videos_name[i]))


@app.route('/next/<video_list_index>/<video_list_length>')
def next_video(video_list_index, video_list_length):
    i = int(video_list_index)+1
    session['video_list_index'] = i
    session['video_list_length'] = int(video_list_length)
    return redirect(url_for('label_page', name=videos_name[i]))


@app.route('/video/<name>')
def video_file_server(name=None):
    path = name2path[name]
    resp = send_file(path, mimetype='video/x-flv')
    return resp


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['video_path'] = video_path
            flash('You were logged in')
            return render_template("video_list.html", videos_name=videos_name)
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return render_template('login.html', error=None)


# 标注的数据传递给数据库
@app.route('/add', methods=['POST'])
def submit_label():
    # first do search
    radio_dict = search_data(session['video_path'], request.form['video_name']+'.'+expansion)
    if len(radio_dict) != 0:
        g.db.execute("update label_set set arousal_level=%d, excitement_level=%d, pleasure_level=%d, "
                     "contentment_level=%d, sleepiness_level=%d, depression_level=%d, misery_level=%d,"
                     "distress_level=%d where video_path='%s' and video_name='%s'" %
                     (int(request.form['arousal']), int(request.form['excitement']), int(request.form['pleasure']),
                      int(request.form['contentment']), int(request.form['sleepiness']), int(request.form['depression']),
                      int(request.form['misery']), int(request.form['distress']), session['video_path'],
                      request.form['video_name']+'.'+expansion))
    else:
        g.db.execute("insert into label_set(video_path,video_name,arousal_level,excitement_level,"
                     "pleasure_level,contentment_level,sleepiness_level,depression_level,misery_level,distress_level)"
                     "values(?,?,?,?,?,?,?,?,?,?)", [session['video_path'], request.form['video_name']+'.'+expansion,
                                                     int(request.form['arousal']), int(request.form['excitement']),
                                                     int(request.form['pleasure']), int(request.form['contentment']),
                                                     int(request.form['sleepiness']), int(request.form['depression']),
                                                     int(request.form['misery']), int(request.form['distress'])])
    g.db.commit()
    flash("Successfully Insert Or Update!")
    return render_template("index.html", name=request.form['video_name'], arousal_level=int(request.form['arousal']),
                           excitement_level=int(request.form['excitement']),
                           pleasure_level=int(request.form['pleasure']),
                           contentment_level=int(request.form['contentment']),
                           sleepiness_level=int(request.form['sleepiness']),
                           depression_level=int(request.form['depression']),
                           misery_level=int(request.form['misery']),
                           distress_level=int(request.form['distress']),
                           video_list_index=int(request.form['video_list_index']),
                           video_list_length=int(request.form['video_list_length']))


if __name__ == '__main__':
    app.run()
