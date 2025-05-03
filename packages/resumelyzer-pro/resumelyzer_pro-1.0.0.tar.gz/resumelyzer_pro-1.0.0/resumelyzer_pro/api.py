from flask import Blueprint, jsonify
from ..models import APIKey, db
from .services import generate_pdf_report

pro_bp = Blueprint('pro', __name__, url_prefix='/pro')

@pro_bp.route('/generate-key/<tier>')
@requires_tier('admin')  # Only admins can generate keys
def generate_key(tier):
    """Generate a new API key"""
    if tier not in ['free', 'pro', 'enterprise']:
        return jsonify({"error": "Invalid tier"}), 400
    
    new_key = APIKey(tier=tier)
    db.session.add(new_key)
    db.session.commit()
    
    return jsonify({
        "key": new_key.key,
        "tier": new_key.tier,
        "requests_remaining": new_key.requests_remaining
    })

@pro_bp.route('/analyze', methods=['POST'])
@requires_tier('pro')
def analyze():
    """Pro tier single file analysis"""
    data = request.json
    result = analyze_resume(data['text'])
    return jsonify(result)

@pro_bp.route('/bulk-analyze', methods=['POST'])
@requires_tier('enterprise')
def bulk_analyze():
    """Enterprise bulk analysis"""
    files = request.json.get('files', [])
    results = [analyze_resume(f['text']) for f in files]
    return jsonify({"results": results})

@pro_bp.route('/generate-report', methods=['POST'])
@requires_tier('pro')
def generate_report():
    """Generate PDF report"""
    analysis = request.json
    pdf = generate_pdf_report(analysis)
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='resume_report.pdf'
    )