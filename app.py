from flask import (
    Flask, render_template, request, redirect,
    url_for, jsonify, abort, session, make_response
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import random
import enum
import json

# ────────────────────────────────────────────────
#  App & DB setup
# ────────────────────────────────────────────────
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trickie.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-me"        # required for session storage
db = SQLAlchemy(app)


# ────────────────────────────────────────────────
#  Model
# ────────────────────────────────────────────────
class ResultEnum(enum.Enum):
    PENDING = "PENDING"
    WIN     = "WIN"
    LOSE    = "LOSE"
    NORMAL  = "NORMAL"


class Trickie(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    slug           = db.Column(db.String(36), unique=True, nullable=False)
    creator_name   = db.Column(db.String(100), nullable=False)
    creator_token  = db.Column(db.String(8), nullable=False)  # NEW FIELD
    amount_cents   = db.Column(db.Integer, nullable=False)
    description    = db.Column(db.String(140), nullable=False)
    wants_double   = db.Column(db.Boolean, default=False)
    result         = db.Column(db.Enum(ResultEnum), default=ResultEnum.PENDING)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


with app.app_context():
    db.create_all()


# ────────────────────────────────────────────────
#  Helper functions
# ────────────────────────────────────────────────
def get_or_create_creator_token(name):
    """
    Get existing creator token from cookies or create a new one
    """
    # Check if we already have creator tokens in cookies
    creator_tokens = json.loads(request.cookies.get('creator_tokens', '{}'))
    
    # If this name already has a token, use it
    if name in creator_tokens:
        return creator_tokens[name]
    
    # Otherwise generate a new one
    return str(uuid4())[:8]


def save_creator_token(response, name, token):
    """
    Save creator token to cookies
    """
    creator_tokens = json.loads(request.cookies.get('creator_tokens', '{}'))
    creator_tokens[name] = token
    
    # Set cookie for 1 year
    response.set_cookie(
        'creator_tokens',
        json.dumps(creator_tokens),
        max_age=365*24*60*60,
        httponly=True
    )
    return response


# ────────────────────────────────────────────────
#  Landing Page
# ────────────────────────────────────────────────
@app.route("/")
def index():
    """Landing page with options to create or view Trickies"""
    # Check if user has any creator tokens - if so, enable My Trickies
    has_trickies = bool(request.cookies.get('creator_tokens', '{}') != '{}')
    return render_template("landing.html", has_trickies=has_trickies)


# ────────────────────────────────────────────────
#  Three-step "Create" flow
# ────────────────────────────────────────────────

# STEP 1 - Name  ────────────────────────────────────
@app.route("/create/name", methods=["GET", "POST"])
def name_step():
    """
    First step: Ask for the creator's name
    """
    if request.method == "POST":
        session["creator_name"] = request.form.get("name", "").strip()[:100]
        return redirect(url_for("amount_step"))
    
    return render_template("name.html")


# STEP 2 - Amount  ──────────────────────────────────
@app.route("/create/amount", methods=["GET", "POST"])
def amount_step():
    """
    Screen that shows the Tikkie-style sentence:
    "Ask everyone to pay me back € …"  (+ optional switch).
    """
    # Guard: user jumped straight in without name
    if "creator_name" not in session:
        return redirect(url_for("name_step"))
    
    if request.method == "POST":
        # keep state in the session until we finish
        session["amount_euros"] = float(request.form.get("amount", 0))
        session["wants_double"] = "wants_double" in request.form
        return redirect(url_for("description_step"))

    return render_template("amount.html")


# STEP 3 - Description  ─────────────────────────────
@app.route("/create/description", methods=["GET", "POST"])
def description_step():
    """
    Screen that asks: "What is it for?" and finally
    creates the Trickie + redirects to the dashboard.
    """
    # Guard: user reloaded or jumped straight in
    if "amount_euros" not in session or "creator_name" not in session:
        return redirect(url_for("name_step"))

    if request.method == "POST":
        description   = request.form.get("description", "")[:140]
        amount_cents  = int(session.pop("amount_euros") * 100)
        wants_double  = session.pop("wants_double", False)
        creator_name  = session.pop("creator_name")
        
        # Get or create creator token
        creator_token = get_or_create_creator_token(creator_name)

        slug = str(uuid4())
        trickie = Trickie(
            slug          = slug,
            creator_name  = creator_name,
            creator_token = creator_token,
            amount_cents  = amount_cents,
            description   = description,
            wants_double  = wants_double
        )
        db.session.add(trickie)
        db.session.commit()

        # Redirect to dashboard and save creator token
        response = make_response(redirect(url_for("dashboard", slug=slug)))
        save_creator_token(response, creator_name, creator_token)
        
        return response

    return render_template("description.html")


# Back-compat: /create redirects to name step
@app.route("/create")
def create_redirect():
    return redirect(url_for("name_step"))


# ────────────────────────────────────────────────
#  My Trickies - Now functional!
# ────────────────────────────────────────────────
@app.route("/my-trickies")
def my_trickies():
    """Redirect to user's trickies based on cookies"""
    creator_tokens = json.loads(request.cookies.get('creator_tokens', '{}'))
    
    if not creator_tokens:
        return render_template("find_trickies.html")
    
    # If user has tokens, redirect to the first one
    # In a real app, you might want to show a list to choose from
    first_name = list(creator_tokens.keys())[0]
    first_token = creator_tokens[first_name]
    
    return redirect(url_for('creator_trickies', 
                          creator_slug=f"{first_name.lower().replace(' ', '-')}-{first_token}"))


@app.route("/my-trickies/<creator_slug>")
def creator_trickies(creator_slug):
    """Show all trickies for a specific creator"""
    # Parse the slug (name-token)
    try:
        parts = creator_slug.rsplit('-', 1)
        if len(parts) != 2:
            abort(404)
        name_part, token = parts
        
        # Find trickies with this token
        trickies = Trickie.query.filter_by(creator_token=token).order_by(Trickie.created_at.desc()).all()
        
        if not trickies:
            abort(404)
            
        creator_name = trickies[0].creator_name
        
        # Calculate stats
        total_requested = sum(t.amount_cents for t in trickies) / 100
        total_won = sum(t.amount_cents * 2 for t in trickies if t.result == ResultEnum.WIN) / 100
        total_lost = len([t for t in trickies if t.result == ResultEnum.LOSE])
        
        return render_template("creator_trickies.html",
                             trickies=trickies,
                             creator_name=creator_name,
                             creator_slug=creator_slug,
                             total_requested=total_requested,
                             total_won=total_won,
                             total_lost=total_lost)
    except:
        abort(404)


@app.route("/find-trickies", methods=["GET", "POST"])
def find_trickies():
    """Help users find their trickies by name"""
    if request.method == "POST":
        search_name = request.form.get("name", "").strip()
        
        # Find all unique creator tokens for this name
        creators = db.session.query(
            Trickie.creator_name, 
            Trickie.creator_token
        ).filter(
            Trickie.creator_name.ilike(f"%{search_name}%")
        ).distinct().all()
        
        return render_template("find_trickies.html", 
                             search_name=search_name,
                             creators=creators)
    
    return render_template("find_trickies.html")


# ────────────────────────────────────────────────
#  Existing routes (updated dashboard)
# ────────────────────────────────────────────────
@app.route("/r/<slug>")
def request_page(slug):
    trickie = Trickie.query.filter_by(slug=slug).first()
    if not trickie:
        abort(404)
    
    # Handle JSON request for status polling
    if request.args.get('json'):
        return jsonify({"result": trickie.result.value})
    
    return render_template("request.html", trickie=trickie)


@app.route("/spin/<slug>", methods=["POST"])
def spin(slug):
    trickie = Trickie.query.filter_by(slug=slug).first() or abort(404)

    if trickie.result != ResultEnum.PENDING:
        return jsonify({"result": trickie.result.value}), 400

    trickie.result = ResultEnum.WIN if random.random() < 0.495 else ResultEnum.LOSE
    db.session.commit()
    
    # Return the result and amount_cents
    return jsonify({
        "result": trickie.result.value,
        "amount_cents": trickie.amount_cents
    })


@app.route("/pay/<slug>", methods=["POST"])
def pay(slug):
    trickie = Trickie.query.filter_by(slug=slug).first() or abort(404)

    if trickie.result == ResultEnum.PENDING:
        trickie.result = ResultEnum.NORMAL
        db.session.commit()

    return redirect(url_for("dashboard", slug=slug))


@app.route("/d/<slug>")
def dashboard(slug):
    trickie = Trickie.query.filter_by(slug=slug).first() or abort(404)
    
    # Generate creator URL for display
    creator_slug = f"{trickie.creator_name.lower().replace(' ', '-')}-{trickie.creator_token}"
    creator_url = url_for('creator_trickies', creator_slug=creator_slug, _external=True)
    
    return render_template("dashboard.html", 
                         trickie=trickie,
                         creator_url=creator_url,
                         creator_slug=creator_slug)


@app.route("/result/<slug>")
def result_page(slug):
    """Show the win/lose result page after spinning"""
    trickie = Trickie.query.filter_by(slug=slug).first()
    if not trickie:
        abort(404)
    
    # Only show result page if the game has been played
    if trickie.result not in [ResultEnum.WIN, ResultEnum.LOSE]:
        return redirect(url_for("request_page", slug=slug))
    
    return render_template("result.html", trickie=trickie)


# ────────────────────────────────────────────────
#  Run
# ────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)