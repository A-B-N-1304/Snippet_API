from flask import Flask, request, jsonify
from models import db, User, Snippet, SnippetVersion
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/users/<user_id>/snippets', methods=['POST'])
def save_snippet(user_id):
    data = request.json
    snippet_name = data['snippet_name']
    language = data['language']
    code = data['code_content']

    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id)
        db.session.add(user)

    snippet = Snippet.query.filter_by(user_id=user_id, name=snippet_name).first()
    if not snippet:
        snippet = Snippet(user_id=user_id, name=snippet_name, language=language)
        db.session.add(snippet)
    else:
        snippet.updated_at = datetime.utcnow()
        snippet.language = language

    db.session.commit()

    version = SnippetVersion(snippet_id=snippet.id, code_content=code)
    db.session.add(version)
    db.session.commit()

    return jsonify({
        "snippet_name": snippet.name,
        "language": snippet.language,
        "updated_at": snippet.updated_at,
        "version_id": version.id
    })

@app.route('/users/<user_id>/snippets/<snippet_name>', methods=['GET'])
def get_snippet(user_id, snippet_name):
    version_id = request.args.get('version_id')
    snippet = Snippet.query.filter_by(user_id=user_id, name=snippet_name).first()
    if not snippet:
        return jsonify({'error': 'Not found'}), 404

    if version_id:
        version = SnippetVersion.query.filter_by(snippet_id=snippet.id, id=version_id).first()
    else:
        version = SnippetVersion.query.filter_by(snippet_id=snippet.id).order_by(SnippetVersion.created_at.desc()).first()

    if not version:
        return jsonify({'error': 'Version not found'}), 404

    return jsonify({
        "snippet_name": snippet.name,
        "language": snippet.language,
        "code_content": version.code_content,
        "updated_at": snippet.updated_at,
        "version_id": version.id
    })

@app.route('/users/<user_id>/snippets', methods=['GET'])
def list_snippets(user_id):
    snippets = Snippet.query.filter_by(user_id=user_id).all()
    result = []
    for s in snippets:
        result.append({
            "snippet_name": s.name,
            "language": s.language,
            "updated_at": s.updated_at
        })
    return jsonify(result)

@app.route('/users/<user_id>/snippets/<snippet_name>', methods=['DELETE'])
def delete_snippet(user_id, snippet_name):
    snippet = Snippet.query.filter_by(user_id=user_id, name=snippet_name).first()
    if not snippet:
        return '', 404
    SnippetVersion.query.filter_by(snippet_id=snippet.id).delete()
    db.session.delete(snippet)
    db.session.commit()
    return '', 204

@app.route('/users/<user_id>/snippets/<snippet_name>/versions', methods=['GET'])
def list_versions(user_id, snippet_name):
    snippet = Snippet.query.filter_by(user_id=user_id, name=snippet_name).first()
    if not snippet:
        return jsonify([])

    versions = SnippetVersion.query.filter_by(snippet_id=snippet.id).all()
    return jsonify([
        {"version_id": v.id, "created_at": v.created_at} for v in versions
    ])

@app.route('/users/<user_id>/snippets/search', methods=['GET'])
def search_snippets(user_id):
    keyword = request.args.get('keyword', '')
    snippets = Snippet.query.filter_by(user_id=user_id).all()
    result = []
    for s in snippets:
        version = SnippetVersion.query.filter_by(snippet_id=s.id).order_by(SnippetVersion.created_at.desc()).first()
        if version and keyword.lower() in version.code_content.lower():
            result.append({
                "snippet_name": s.name,
                "language": s.language,
                "updated_at": s.updated_at
            })
    return jsonify(result)
