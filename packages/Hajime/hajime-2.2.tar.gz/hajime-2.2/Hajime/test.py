from core import *

app = Hajime()
@app.route("/")
def main(environ):
    return app.template("index.html")

app.launch(
    5900,
    5901
)