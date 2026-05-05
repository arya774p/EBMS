from routes.auth_routes import register_auth_routes
from routes.customer_routes import register_customer_routes
from routes.admin_routes import register_admin_routes


def register_all_routes(app):
    register_auth_routes(app)
    register_customer_routes(app)
    register_admin_routes(app)