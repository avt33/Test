from flask import Blueprint, render_template

DCF_bp = Blueprint('DCF', __name__)

@DCF_bp.route("/dcf")
def dcf():
    return render_template("DCF.html")