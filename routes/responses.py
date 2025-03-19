from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import prisma

responses_bp = Blueprint('responses', __name__)

@responses_bp.route('/forms/<int:form_id>/responses', methods=['POST'])
async def submit_response(form_id):
    try:
        data = request.get_json()

        # Verify form exists and is published
        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'isPublished': True
            },
            include={
                'questions': True
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found or not published'
            }), 404

        # Validate required questions are answered
        required_questions = {q.id for q in form.questions if q.isRequired}
        answered_questions = {a['question_id'] for a in data['answers']}
        missing_required = required_questions - answered_questions

        if missing_required:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required answers'
            }), 400

        # Create response and answers
        response = await prisma.response.create(
            data={
                'formId': form_id,
                'respondentEmail': data.get('respondent_email'),
                'answers': {
                    'create': [{
                        'questionId': answer['question_id'],
                        'textAnswer': answer['text_answer']
                    } for answer in data['answers']]
                }
            }
        )

        return jsonify({
            'response_id': response.id,
            'submitted_at': response.submittedAt.isoformat(),
            'message': 'Response submitted successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400

@responses_bp.route('/forms/<int:form_id>/responses', methods=['GET'])
@jwt_required()
async def get_responses(form_id):
    try:
        user_id = get_jwt_identity()

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

        responses = await prisma.response.find_many(
            where={'formId': form_id},
            include={
                'answers': {
                    'include': {
                        'question': True
                    }
                }
            }
        )

        return jsonify({
            'responses': [{
                'response_id': r.id,
                'respondent_email': r.respondentEmail,
                'submitted_at': r.submittedAt.isoformat(),
                'answers': [{
                    'question_id': a.questionId,
                    'question_text': a.question.questionText,
                    'text_answer': a.textAnswer
                } for a in r.answers]
            } for r in responses]
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@responses_bp.route('/<int:response_id>', methods=['GET'])
@jwt_required()
async def get_response(response_id):
    try:
        user_id = get_jwt_identity()

        response = await prisma.response.find_unique(
            where={'id': response_id},
            include={
                'form': True,
                'answers': {
                    'include': {
                        'question': True
                    }
                }
            }
        )

        if not response or response.form.userId != user_id:
            return jsonify({
                'error': 'Not Found',
                'message': 'Response not found'
            }), 404

        return jsonify({
            'response_id': response.id,
            'form_id': response.formId,
            'respondent_email': response.respondentEmail,
            'submitted_at': response.submittedAt.isoformat(),
            'answers': [{
                'question_id': a.questionId,
                'question_text': a.question.questionText,
                'text_answer': a.textAnswer
            } for a in response.answers]
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@responses_bp.route('/<int:response_id>', methods=['DELETE'])
@jwt_required()
async def delete_response(response_id):
    try:
        user_id = get_jwt_identity()

        response = await prisma.response.find_unique(
            where={'id': response_id},
            include={'form': True}
        )

        if not response or response.form.userId != user_id:
            return jsonify({
                'error': 'Not Found',
                'message': 'Response not found'
            }), 404

        await prisma.response.delete(
            where={'id': response_id}
        )

        return jsonify({
            'message': 'Response deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500 