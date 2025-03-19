# Form Management API

A Flask-based REST API for managing forms, questions, and responses. Built with Flask, Prisma ORM, and JWT authentication.

## Features

- User Authentication (Register, Login, Logout)
- Form Management (CRUD operations)
- Question Management (Add, Update, Delete, Reorder)
- Response Collection and Management
- Analytics and Reporting
- Excel Export

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```
DATABASE_URL="file:./dev.db"
JWT_SECRET_KEY="your-secret-key"
```

5. Initialize the database:
```bash
prisma db push
```

6. Generate Prisma client:
```bash
prisma generate
```

7. Run the application:
```bash
python app.py
```

## API Documentation

### Authentication APIs

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Form Management APIs

- `POST /api/v1/forms` - Create new form
- `GET /api/v1/forms` - Get all forms
- `GET /api/v1/forms/{form_id}` - Get form by ID
- `PUT /api/v1/forms/{form_id}` - Update form
- `DELETE /api/v1/forms/{form_id}` - Delete form
- `PUT /api/v1/forms/{form_id}/publish` - Publish/unpublish form

### Question Management APIs

- `POST /api/v1/forms/{form_id}/questions` - Add question to form
- `GET /api/v1/forms/{form_id}/questions` - Get all questions for form
- `PUT /api/v1/questions/{question_id}` - Update question
- `DELETE /api/v1/questions/{question_id}` - Delete question
- `PUT /api/v1/forms/{form_id}/questions/reorder` - Reorder questions

### Response Management APIs

- `POST /api/v1/forms/{form_id}/responses` - Submit form response
- `GET /api/v1/forms/{form_id}/responses` - Get all responses for form
- `GET /api/v1/responses/{response_id}` - Get response by ID
- `DELETE /api/v1/responses/{response_id}` - Delete response

### Analytics APIs

- `GET /api/v1/forms/{form_id}/analytics/summary` - Get form response summary
- `GET /api/v1/questions/{question_id}/analytics` - Get answers for specific question
- `GET /api/v1/forms/{form_id}/export` - Export form responses to Excel

## Error Handling

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
    "error": "Error Type",
    "message": "Detailed error message"
}
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Development

To run the application in development mode:

```bash
export FLASK_ENV=development
export FLASK_APP=app.py
flask run
```

## License

MIT
