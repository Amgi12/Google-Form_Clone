from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import prisma
from collections import Counter
from datetime import datetime, timedelta
import pandas as pd
import io

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/forms/<int:form_id>/analytics/summary', methods=['GET'])
@jwt_required()
async def get_form_summary(form_id):
    try:
        user_id = get_jwt_identity()

        # Verify form ownership
        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            },
            include={
                'responses': True
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        if not form.responses:
            return jsonify({
                'total_responses': 0,
                'response_rate_per_day': [],
                'first_response_at': None,
                'latest_response_at': None
            }), 200

        # Calculate response statistics
        responses = sorted(form.responses, key=lambda x: x.submittedAt)
        first_response = responses[0]
        latest_response = responses[-1]

        # Calculate response rate per day
        date_counts = Counter(r.submittedAt.date() for r in responses)
        response_rate = [
            {
                'date': date.isoformat(),
                'count': count
            }
            for date, count in sorted(date_counts.items())
        ]

        return jsonify({
            'total_responses': len(responses),
            'response_rate_per_day': response_rate,
            'first_response_at': first_response.submittedAt.isoformat(),
            'latest_response_at': latest_response.submittedAt.isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@analytics_bp.route('/questions/<int:question_id>/analytics', methods=['GET'])
@jwt_required()
async def get_question_analytics(question_id):
    try:
        user_id = get_jwt_identity()

        # Verify question ownership through form
        question = await prisma.question.find_unique(
            where={'id': question_id},
            include={
                'form': True,
                'answers': True
            }
        )

        if not question or question.form.userId != user_id:
            return jsonify({
                'error': 'Not Found',
                'message': 'Question not found'
            }), 404

        if not question.answers:
            return jsonify({
                'total_answers': 0,
                'common_answers': []
            }), 200

        # Calculate answer statistics
        answer_counts = Counter(a.textAnswer for a in question.answers)
        common_answers = [
            {
                'text_answer': answer,
                'count': count
            }
            for answer, count in answer_counts.most_common()
        ]

        return jsonify({
            'total_answers': len(question.answers),
            'common_answers': common_answers
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@analytics_bp.route('/forms/<int:form_id>/export', methods=['GET'])
@jwt_required()
async def export_form_responses(form_id):
    try:
        user_id = get_jwt_identity()

        # Verify form ownership
        form = await prisma.form.find_first(
            where={
                'id': form_id,
                'userId': user_id
            },
            include={
                'questions': True,
                'responses': {
                    'include': {
                        'answers': True
                    }
                }
            }
        )

        if not form:
            return jsonify({
                'error': 'Not Found',
                'message': 'Form not found'
            }), 404

        # Prepare data for export
        data = []
        for response in form.responses:
            row = {
                'Response ID': response.id,
                'Respondent Email': response.respondentEmail,
                'Submitted At': response.submittedAt.isoformat()
            }
            
            # Add answers to the row
            answer_dict = {a.questionId: a.textAnswer for a in response.answers}
            for question in form.questions:
                row[question.questionText] = answer_dict.get(question.id, '')
            
            data.append(row)

        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'form_{form_id}_responses.xlsx'
        )

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500 