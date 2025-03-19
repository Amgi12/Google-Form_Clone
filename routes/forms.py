from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import prisma
from datetime import datetime

forms_bp = Blueprint('forms', __name__)

@forms_bp.route('', methods=['POST'])
@jwt_required()
async def create_form():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        form = await prisma.form.create(
            data={
                'title': data['title'],
                'description': data.get('description'),
                'userId': user_id
            }
        )

        return jsonify({
            'form_id': form.id,
            'title': form.title,
            'description': form.description,
            'created_at': form.createdAt.isoformat(),
            'is_published': form.isPublished
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400

@forms_bp.route('', methods=['GET'])
@jwt_required()
async def get_all_forms():
    try:
        user_id = get_jwt_identity()
        forms = await prisma.form.find_many(
            where={'userId': user_id},
            include={
                'responses': True
            }
        )

        return jsonify({
            'forms': [{
                'form_id': form.id,
                'title': form.title,
                'created_at': form.createdAt.isoformat(),
                'is_published': form.isPublished,
                'response_count': len(form.responses)
            } for form in forms]
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@forms_bp.route('/<int:form_id>', methods=['GET'])
@jwt_required()
async def get_form(form_id):
    try:
        user_id = get_jwt_identity()
        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            },
            include={
                'questions': True
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        return jsonify({
            'form_id': form.id,
            'title': form.title,
            'description': form.description,
            'created_at': form.createdAt.isoformat(),
            'is_published': form.isPublished,
            'questions': [{
                'question_id': q.id,
                'question_text': q.questionText,
                'is_required': q.isRequired,
                'display_order': q.displayOrder
            } for q in form.questions]
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@forms_bp.route('/<int:form_id>', methods=['PUT'])
@jwt_required()
async def update_form(form_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        updated_form = await prisma.form.update(
            where={'id': form_id},
            data={
                'title': data.get('title', form.title),
                'description': data.get('description', form.description)
            }
        )

        return jsonify({
            'form_id': updated_form.id,
            'title': updated_form.title,
            'description': updated_form.description,
            'updated_at': updated_form.updatedAt.isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@forms_bp.route('/<int:form_id>', methods=['DELETE'])
@jwt_required()
async def delete_form(form_id):
    try:
        user_id = get_jwt_identity()
        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        await prisma.form.delete(
            where={'id': form_id}
        )

        return jsonify({
            'message': 'Form deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@forms_bp.route('/<int:form_id>/publish', methods=['PUT'])
@jwt_required()
async def toggle_form_publish(form_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        is_published = data.get('is_published', True)

        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        updated_form = await prisma.form.update(
            where={'id': form_id},
            data={'isPublished': is_published}
        )

        return jsonify({
            'form_id': updated_form.id,
            'is_published': updated_form.isPublished,
            'message': f'Form {"published" if is_published else "unpublished"} successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500 