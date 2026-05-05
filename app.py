import click
from config import Config
from flask import Flask, g, render_template
from flask_login import current_user
from extensions import db, bcrypt, login_manager
from routes import register_all_routes
from services.account_service import create_admin_user
from utils.query_logger import ensure_query_log_table, install_query_logger
from utils.template_helpers import register_template_helpers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view="login"
    login_manager.login_message = "Please login to continue."
    
    @app.route('/')
    def home():
        return render_template("home.html")

    @app.before_request
    def remember_query_context():
        g.query_user_id = None
        g.query_user_role = None
        if current_user.is_authenticated:
            g.query_user_id = current_user.id
            g.query_user_role = current_user.role

    @app.cli.command("create-admin")
    @click.option("--email", default="admin@gmail.com", show_default=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin_command(email, password):
        """Create one admin account from the terminal."""
        try:
            create_admin_user(email, password)
            click.echo(f"Admin created: {email}")
        except ValueError as error:
            click.echo(str(error))

    register_template_helpers(app)
    ensure_query_log_table(app)
    install_query_logger(app)
    register_all_routes(app)
    
    return app

myapp = create_app()
if __name__ == "__main__" :
    myapp.run(debug=True)
    
