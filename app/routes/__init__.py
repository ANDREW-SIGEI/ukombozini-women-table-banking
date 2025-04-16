from flask import Blueprint
from . import (
    auth, main, api, financial, collections, 
    accounting, meetings, products, settings,
    groups, members, field_officers
)

# Create a list of all blueprints and their URL prefixes
blueprints = [
    (auth.bp, '/auth'),
    (main.bp, '/'),
    (api.bp, '/api'),
    (financial.bp, '/financial'),
    (collections.bp, '/collections'),
    (accounting.bp, '/accounting'),
    (meetings.bp, '/meetings'),
    (products.bp, '/products'),
    (settings.bp, '/settings'),
    (groups.bp, '/groups'),
    (members.bp, '/members'),
    (field_officers.field_officers_bp, '/field-officers')
]

def init_app(app):
    """Register all blueprints with the app"""
    # Initialize default settings
    settings.init_default_settings()
    
    # Register blueprints
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix) 