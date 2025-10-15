from __future__ import annotations
from backend import create_app

# WSGI entrypoint compatible with Gunicorn
application = create_app()

# Some servers look for `app`
app = application

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
