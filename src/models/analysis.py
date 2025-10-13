from src.models import db  # Import the shared db instance
from datetime import datetime
import json

class CompanyAnalysis(db.Model):
    """Model for storing company AI visibility analyses"""
    __tablename__ = 'company_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    insights = db.Column(db.Text)
    platform_scores = db.Column(db.Text)  # JSON stored as text
    
    def set_platform_scores(self, platform, scores):
        """Set scores for a specific platform"""
        current_scores = json.loads(self.platform_scores) if self.platform_scores else {}
        current_scores[platform] = scores
        self.platform_scores = json.dumps(current_scores)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'analysis_date': self.analysis_date.isoformat(),
            'insights': self.insights,
            'platform_scores': json.loads(self.platform_scores) if self.platform_scores else {}
        }
