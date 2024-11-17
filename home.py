from flask import Flask, Blueprint, render_template
from FCF import FCF_bp
from DCF import DCF_bp

app = Flask(__name__)
app.register_blueprint(FCF_bp)
app.register_blueprint(DCF_bp)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True);