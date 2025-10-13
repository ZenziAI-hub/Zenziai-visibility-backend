from flask import Blueprint, jsonify, request
from src.models.analysis import CompanyAnalysis, db
from src.services.ai_analyzer import AIAnalyzer
import json
import requests  
from bs4 import BeautifulSoup  

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_company():
    """Analyze a company's AI visibility across platforms"""
    try:
        data = request.json
        company_name = data.get('company_name', '').strip()
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Check if analysis already exists for this company (within last 24 hours)
        existing_analysis = CompanyAnalysis.query.filter_by(company_name=company_name).first()
        
        if existing_analysis:
            return jsonify({
                'message': 'Analysis found in cache',
                'data': existing_analysis.to_dict()
            }), 200
        
        # Perform new analysis
        analyzer = AIAnalyzer()
        analysis_results = analyzer.analyze_company(company_name)
        
        # Save to database
        analysis = CompanyAnalysis(
            company_name=company_name,
            insights=analysis_results.get('insights', '')
        )
        
        # Set platform scores
        for platform, scores in analysis_results.get('platform_scores', {}).items():
            analysis.set_platform_scores(platform, scores)
        
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'data': analysis.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get a specific analysis by ID"""
    analysis = CompanyAnalysis.query.get_or_404(analysis_id)
    return jsonify(analysis.to_dict())

@analysis_bp.route('/analysis/company/<company_name>', methods=['GET'])
def get_company_analysis(company_name):
    """Get the latest analysis for a specific company"""
    analysis = CompanyAnalysis.query.filter_by(company_name=company_name).order_by(CompanyAnalysis.analysis_date.desc()).first()
    
    if not analysis:
        return jsonify({'error': 'No analysis found for this company'}), 404
    
    return jsonify(analysis.to_dict())

@analysis_bp.route('/analysis', methods=['GET'])
def get_all_analyses():
    """Get all analyses with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    analyses = CompanyAnalysis.query.order_by(CompanyAnalysis.analysis_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'analyses': [analysis.to_dict() for analysis in analyses.items],
        'total': analyses.total,
        'pages': analyses.pages,
        'current_page': page
    })

@analysis_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get list of supported AI platforms"""
    platforms = [
        {'name': 'ChatGPT', 'id': 'chatgpt', 'provider': 'OpenAI'},
        {'name': 'Claude', 'id': 'claude', 'provider': 'Anthropic'},
        {'name': 'Perplexity AI', 'id': 'perplexity', 'provider': 'Perplexity'},
        {'name': 'Arc Search', 'id': 'arc_search', 'provider': 'The Browser Company'},
        {'name': 'SearchGPT', 'id': 'searchgpt', 'provider': 'OpenAI'}
    ]
    return jsonify(platforms)

@analysis_bp.route('/methodologies', methods=['GET'])
def get_methodologies():
    """Get list of ranking methodologies"""
    methodologies = [
        {
            'id': 'cidr',
            'name': 'CIDR',
            'full_name': 'Contextual Intent-Driven Ranking',
            'description': 'How well do LLMs understand the intent behind queries related to this company?'
        },
        {
            'id': 'scvs',
            'name': 'SCVS',
            'full_name': 'Source Credibility & Verifiability Score',
            'description': 'How well is the company represented in verifiable, reputable, and cited sources?'
        },
        {
            'id': 'acso',
            'name': 'ACSO',
            'full_name': 'Adaptive Content Structure Optimization',
            'description': 'Is the company\'s online content structured in a way that\'s easy for AI to parse and summarize?'
        },
        {
            'id': 'uifl',
            'name': 'UIFL',
            'full_name': 'User Interaction & Feedback Loop',
            'description': 'How often is this company positively engaged with through AI tools (clicks, follow-ups, thumbs up)?'
        }
    ]
    return jsonify(methodologies)

@analysis_bp.route('/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze a specific URL for AI visibility factors"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title and meta description for initial analysis
        title = soup.title.string if soup.title else 'No title found'
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_description_content = meta_description['content'] if meta_description else 'No meta description found'
        
        # Placeholder for actual analysis logic
        analysis_results = {
            "url": url,
            "overall_score": {
                "value": 50,
                "interpretation": "Initial analysis based on basic content extraction."
            },
            "content_quality": {
                "score": 0,
                "findings": [
                    f"Page Title: {title}",
                    f"Meta Description: {meta_description_content}",
                    "Further content quality analysis pending."
                ]
            },
            "relevance_and_intent": {
                "score": 0,
                "findings": ["Further relevance and intent analysis pending."]
            },
            "source_credibility": {
                "score": 0,
                "findings": ["Further source credibility analysis pending."]
            },
            "content_structure": {
                "score": 0,
                "findings": ["Further content structure analysis pending."]
            },
            "freshness_and_timeliness": {
                "score": 0,
                "findings": ["Further freshness and timeliness analysis pending."]
            },
            "user_engagement_potential": {
                "score": 0,
                "findings": ["Further user engagement potential analysis pending."]
            },
            "technical_seo": {
                "score": 0,
                "findings": ["Further technical SEO analysis pending."]
            }
        }
        
        return jsonify(analysis_results)
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
