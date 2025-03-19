from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from app import prisma

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
async def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        # Check if user already exists
        existing_user = await prisma.user.find_unique(
            where={'email': email}
        )
        if existing_user:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Email already in use'
            }), 400

        # Create new user
        hashed_password = generate_password_hash(password)
        user = await prisma.user.create(
            data={
                'email': email,
                'password': hashed_password,
                'name': full_name
            }
        )

        return jsonify({
            'user_id': user.id,
            'email': user.email,
            'full_name': user.name,
            'message': 'User registered successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
async def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = await prisma.user.find_unique(
            where={'email': email}
        )

        if not user or not check_password_hash(user.password, password):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid credentials'
            }), 401

        access_token = create_access_token(identity=user.id)
        return jsonify({
            'user_id': user.id,
            'token': access_token,
            'message': 'Login successful'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
async def logout():
    try:
        # In a real application, you might want to blacklist the token here
        return jsonify({
            'message': 'Logout successful'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500 