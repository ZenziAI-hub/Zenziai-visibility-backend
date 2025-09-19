from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import logging

app = Flask(__name__)

# Database Configuration 
database_url = os.environ.get("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///ai_visibility.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Initialize extensions (ONLY ONCE)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class AIInteraction(db.Model):
    __tablename__ = 'ai_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    ai_model = db.Column(db.String(100), nullable=False)
    context = db.Column(db.Text)  # Additional context about the interaction
    rating = db.Column(db.Integer)  # User rating of the response (1-5)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'ai_model': self.ai_model,
            'context': self.context,
            'rating': self.rating
        }

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get recent interactions
        recent_interactions = AIInteraction.query.order_by(
            AIInteraction.timestamp.desc()
        ).limit(10).all()
        
        # Get statistics
        total_interactions = AIInteraction.query.count()
        avg_rating = db.session.query(db.func.avg(AIInteraction.rating)).scalar()
        
        stats = {
            'total_interactions': total_interactions,
            'avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'recent_count': len(recent_interactions)
        }
        
        return render_template('index.html', 
                             interactions=recent_interactions, 
                             stats=stats)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash('Error loading dashboard data', 'error')
        return render_template('index.html', interactions=[], stats={})

@app.route('/log_interaction', methods=['POST'])
def log_interaction():
    """Log a new AI interaction"""
    try:
        data = request.get_json()
        
        interaction = AIInteraction(
            user_input=data.get('user_input', ''),
            ai_response=data.get('ai_response', ''),
            ai_model=data.get('ai_model', 'Unknown'),
            context=data.get('context', ''),
            rating=data.get('rating')
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Interaction logged successfully',
            'interaction_id': interaction.id
        })
        
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Error logging interaction: {str(e)}'
        }), 500

@app.route('/interactions')
def view_interactions():
    """View all interactions with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Number of interactions per page
        
        interactions = AIInteraction.query.order_by(
            AIInteraction.timestamp.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('interactions.html', interactions=interactions)
        
    except Exception as e:
        logger.error(f"Error viewing interactions: {e}")
        flash('Error loading interactions', 'error')
        return redirect(url_for('index'))

@app.route('/interaction/<int:interaction_id>')
def view_interaction(interaction_id):
    """View a specific interaction"""
    try:
        interaction = AIInteraction.query.get_or_404(interaction_id)
        return render_template('interaction_detail.html', interaction=interaction)
        
    except Exception as e:
        logger.error(f"Error viewing interaction {interaction_id}: {e}")
        flash('Interaction not found', 'error')
        return redirect(url_for('view_interactions'))

@app.route('/rate_interaction/<int:interaction_id>', methods=['POST'])
def rate_interaction(interaction_id):
    """Rate an AI interaction"""
    try:
        interaction = AIInteraction.query.get_or_404(interaction_id)
        rating = request.form.get('rating', type=int)
        
        if rating and 1 <= rating <= 5:
            interaction.rating = rating
            db.session.commit()
            flash('Rating saved successfully', 'success')
        else:
            flash('Invalid rating. Please select a rating between 1 and 5.', 'error')
            
        return redirect(url_for('view_interaction', interaction_id=interaction_id))
        
    except Exception as e:
        logger.error(f"Error rating interaction {interaction_id}: {e}")
        flash('Error saving rating', 'error')
        return redirect(url_for('view_interactions'))

@app.route('/api/interactions')
def api_interactions():
    """API endpoint to get interactions as JSON"""
    try:
        interactions = AIInteraction.query.order_by(
            AIInteraction.timestamp.desc()
        ).limit(100).all()
        
        return jsonify([interaction.to_dict() for interaction in interactions])
        
    except Exception as e:
        logger.error(f"Error in API interactions: {e}")
        return jsonify({'error': 'Failed to fetch interactions'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Database initialization
def create_tables():
    """Create database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

if __name__ == '__main__':
    # Create tables on startup
    create_tables()
    
    # Get port from environment variable (Render uses PORT)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
