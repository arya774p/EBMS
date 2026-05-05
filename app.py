from config import Config
from flask import Flask, render_template
from extensions import db, bcrypt, login_manager
from models import Customer
from routes import register_all_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view="login"
    
    @app.route('/')
    def home():
        return render_template("home.html")
    register_all_routes(app)
    
    return app

myapp = create_app()
if __name__ == "__main__" :
    myapp.run(debug=True)
    