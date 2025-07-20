from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String, primary_key = True)

class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String, db.ForeignKey('user_id'), nullable = False)
    name = db.Column(db.String, nullable = False)
    language = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, default = datetime.utcnow)
    
    user = db.relationship('User', backref = db.backref('snippets', lazy = True))
    __table_args__ = (db.UniqueConstraint('user_id', 'name'),)

class SnippetVersion(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    snippet_id = db.Column(db.Integer, db.ForeignKey('snippet.id'), nullable = False)
    code_content = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    snippet = db.relationship('Snippet', backref = db.backref('versions', lazy = True))
