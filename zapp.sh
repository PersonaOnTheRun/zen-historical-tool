$HOME/redis/src/redis-server &&
celery worker -A $HOME/dropbox/projects/flask-easy-zen/app.celery --loglevel=info && 
python3 $HOME/dropbox/projects/flask-easy-zen/app.py
