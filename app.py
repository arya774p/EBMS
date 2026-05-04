from config import Config
from flask import Flask, render_template
from extensions import db
from models import Customer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    @app.route('/')
    def home():
        return render_template("home.html")
    @app.route("/test-db")
    def test_db():
        count = Customer.query.count()
        return f"MySQL connected successfully. Total customers : {count}"
    @app.route("/customers")
    def customers():
        customers = Customer.query.all()
        return render_template("customer.html", customers = customers)
    
    return app
myapp = create_app()
if __name__ == "__main__" :
    myapp.run(debug=True)
    