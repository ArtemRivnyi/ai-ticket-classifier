from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@main_bp.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html")

@main_bp.route("/evaluation")
def evaluation():
    """Render the evaluation page."""
    return render_template("evaluation.html")

@main_bp.route("/dashboard")
def dashboard():
    """Dashboard page"""
    return render_template("dashboard.html")

@main_bp.route("/billing")
def billing():
    """Billing page"""
    return render_template("billing.html")

@main_bp.route("/login")
def login():
    """Login page"""
    return render_template("login.html")

@main_bp.route("/register")
def register():
    """Register page"""
    return render_template("register.html")

@main_bp.route("/contact")
def contact():
    """Contact page"""
    return render_template("contact.html")

@main_bp.route("/privacy")
def privacy():
    """Privacy Policy page"""
    return render_template("privacy.html")

@main_bp.route("/terms")
def terms():
    """Terms of Service page"""
    return render_template("terms.html")

@main_bp.route("/cookies")
def cookies():
    """Cookie Policy page"""
    return render_template("cookies.html")
