## install flask
``` bash
$ pip3 install flask
```
## enable [DEBUG mode](http://flask.pocoo.org/docs/1.0/quickstart/#debug-mode)
``` bash
$ export FLASK_ENV=development
```

## run the application
``` bash
$ export FLASK_APP=hello.py
$ flask run --host=0.0.0.0
```

# Trouble shoot
Console:
    DemuxException: type = CodecUnsupported, info = Flv: Unsupported codec in video frame: 2

[solved](https://github.com/Bilibili/flv.js/issues/47)