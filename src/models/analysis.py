from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class CompanyAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Platform scores (JSON format)
    chatgpt_scores = db.Column(db.Text)  # JSON string containing CIDR, SCVS, ACSO, UIFL scores
    claude_scores = db.Column(db.Text)
    perplexity_scores = db.Column(db.Text)
    arc_search_scores = db.Column(db.Text)
    searchgpt_scores = db.Column(db.Text)
    
    # Overall insights
    insights = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CompanyAnalysis {self.company_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'analysis_date': self.analysis_date.isoformat(),
            'chatgpt_scores': json.loads(self.chatgpt_scores) if self.chatgpt_scores else {},
            'claude_scores': json.loads(self.claude_scores) if self.claude_scores else {},
            'perplexity_scores': json.loads(self.perplexity_scores) if self.perplexity_scores else {},
            'arc_search_scores': json.loads(self.arc_search_scores) if self.arc_search_scores else {},
            'searchgpt_scores': json.loads(self.searchgpt_scores) if self.searchgpt_scores else {},
            'insights': self.insights
        }
    
    def set_platform_scores(self, platform, scores):
        """Set scores for a specific platform"""
        scores_json = json.dumps(scores)
        if platform.lower() == 'chatgpt':
            self.chatgpt_scores = scores_json
        elif platform.lower() == 'claude':
            self.claude_scores = scores_json
        elif platform.lower() == 'perplexity':
            self.perplexity_scores = scores_json
        elif platform.lower() == 'arc_search':
            self.arc_search_scores = scores_json
        elif platform.lower() == 'searchgpt':
            self.searchgpt_scores = scores_json

