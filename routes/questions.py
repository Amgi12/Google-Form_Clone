from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import prisma

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/forms/<int:form_id>/questions', methods=['POST'])
@jwt_required()
async def add_question(form_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Verify form ownership
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

        # Get the current highest display order
        existing_questions = await prisma.question.find_many(
            where={'formId': form_id},
            order={'displayOrder': 'desc'},
            take=1
        )
        next_display_order = (existing_questions[0].displayOrder + 1) if existing_questions else 1

        question = await prisma.question.create(
            data={
                'questionText': data['question_text'],
                'isRequired': data.get('is_required', False),
                'displayOrder': next_display_order,
                'formId': form_id
            }
        )

        return jsonify({
            'question_id': question.id,
            'form_id': question.formId,
            'question_text': question.questionText,
            'is_required': question.isRequired,
            'display_order': question.displayOrder
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400

@questions_bp.route('/forms/<int:form_id>/questions', methods=['GET'])
@jwt_required()
async def get_questions(form_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify form ownership
        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            },
            include={
                'questions': {
                    'orderBy': {
                        'displayOrder': 'asc'
                    }
                }
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        return jsonify({
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

@questions_bp.route('/<int:question_id>', methods=['PUT'])
@jwt_required()
async def update_question(question_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Verify question ownership through form
        question = await prisma.question.find_unique(
            where={'id': question_id},
            include={'form': True}
        )

        if not question or question.form.userId != user_id:
            return jsonify({
                'error': 'Not Found',
                'message': 'Question not found'
            }), 404

        updated_question = await prisma.question.update(
            where={'id': question_id},
            data={
                'questionText': data.get('question_text', question.questionText),
                'isRequired': data.get('is_required', question.isRequired)
            }
        )

        return jsonify({
            'question_id': updated_question.id,
            'question_text': updated_question.questionText,
            'is_required': updated_question.isRequired
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@questions_bp.route('/<int:question_id>', methods=['DELETE'])
@jwt_required()
async def delete_question(question_id):
    try:
        user_id = get_jwt_identity()

        # Verify question ownership through form
        question = await prisma.question.find_unique(
            where={'id': question_id},
            include={'form': True}
        )

        if not question or question.form.userId != user_id:
            return jsonify({
                'error': 'Not Found',
                'message': 'Question not found'
            }), 404

        await prisma.question.delete(
            where={'id': question_id}
        )

        return jsonify({
            'message': 'Question deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@questions_bp.route('/forms/<int:form_id>/questions/reorder', methods=['PUT'])
@jwt_required()
async def reorder_questions(form_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Verify form ownership
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

        # Update each question's display order
        for question_order in data:
            await prisma.question.update(
                where={'id': question_order['question_id']},
                data={'displayOrder': question_order['display_order']}
            )

        return jsonify({
            'message': 'Questions reordered successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400 