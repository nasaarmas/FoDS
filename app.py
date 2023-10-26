from flask import redirect, url_for
from src import app

app.secret_key = "super secret key"


@app.route('/')
def index():
    return redirect(url_for('login.login'))


if __name__ == "__main__":
    app.run(debug=True)
