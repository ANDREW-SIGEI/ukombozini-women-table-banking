from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    csrf.init_app(app)
    
    # Add custom Jinja filters
    from app.utils.jinja_filters import nl2br
    app.jinja_env.filters['nl2br'] = nl2br
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from app.routes import (
        main, auth, meetings, groups, members, dashboard,
        financial, collections, accounting, settings
    )
    from app.routes.products import products_bp
    from app.routes.field_officers import field_officers_bp
    from app.routes.field_officers_web import bp as field_officers_web_bp
    from app.routes.reports import reports_bp
    
    # Register blueprints with proper URL prefixes
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(meetings.bp, url_prefix='/meetings')
    app.register_blueprint(groups.bp, url_prefix='/groups')
    app.register_blueprint(members.bp, url_prefix='/members')
    app.register_blueprint(dashboard.bp, url_prefix='/dashboard')
    app.register_blueprint(financial.bp, url_prefix='/financial')
    app.register_blueprint(collections.bp, url_prefix='/collections')
    app.register_blueprint(accounting.bp, url_prefix='/accounting')
    app.register_blueprint(settings.bp, url_prefix='/settings')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(field_officers_bp, url_prefix='/field-officers')
    app.register_blueprint(field_officers_web_bp, url_prefix='/field-officers-web')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app 