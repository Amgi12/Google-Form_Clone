from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from prisma import Prisma

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
jwt = JWTManager(app)

# Initialize Prisma client
prisma = Prisma()

# Import routes after app initialization to avoid circular imports
from routes.auth import auth_bp
from routes.forms import forms_bp
from routes.questions import questions_bp
from routes.responses import responses_bp
from routes.analytics import analytics_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(forms_bp, url_prefix='/api/v1/forms')
app.register_blueprint(questions_bp, url_prefix='/api/v1/questions')
app.register_blueprint(responses_bp, url_prefix='/api/v1/responses')
app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')

@app.before_request
async def before_request():
    await prisma.connect()

@app.teardown_appcontext
async def teardown_appcontext(exception):
    await prisma.disconnect()

if __name__ == '__main__':
    app.run(debug=True) 