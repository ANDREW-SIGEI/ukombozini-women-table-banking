from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate  # <-- Import Flask-Migrate

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/table_banking'
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # <-- Add this line to initialize Flask-Migrate

# Define models matching your sidebar functionality
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    # Add more fields as needed

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    # Add more fields as needed

@app.route('/api/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': m.id, 'name': m.name} for m in members])

if __name__ == '__main__':
    app.run(debug=True)
