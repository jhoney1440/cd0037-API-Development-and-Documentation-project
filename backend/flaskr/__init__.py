import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    with app.app_context(): 
        setup_db(app)
    CORS(app)


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = {}
        categories_result = Category.query.all() 

        for i in categories_result:
            categories[i.id] = i.type

        return jsonify({
            'categories': categories,
            'success': True
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        questions = Question.query.paginate(page=page, per_page=10)
        question_list = []
        for question in questions:
            question_list.append({'id': question.id, 'question': question.question, 'category':question.category, 'difficulty':question.difficulty, 'answer': question.answer})

        categories = {}
        categories_result = Category.query.all() 

        for i in categories_result:
            categories[i.id] = i.type
        

        return jsonify({
            'questions': question_list,
            'total_pages': questions.pages,
            'total_questions': questions.total,
            'categories': categories,
            'current_category': '1',
            'success': True
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({'message': 'Question deleted successfully', 'success': True}), 200


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        # Get the question data from the request
        question_data = request.get_json()

        # Extract the required fields from the question data
        question_text = question_data.get('question')
        answer_text = question_data.get('answer')
        category = question_data.get('category')
        difficulty = question_data.get('difficulty')

        # Validate that all required fields are present in the request
        if not all([question_text, answer_text, category, difficulty]):
            return jsonify({'error': 'Missing required fields.'}), 400

        # Create a new Question object
        new_question = Question(
            question=question_text,
            answer=answer_text,
            category=category,
            difficulty=difficulty
        )

        # Add the new question to the database
        db.session.add(new_question)
        db.session.commit()

        # Return a success message and the new question data
        return jsonify({'success': True, 'question': {
            'id': new_question.id,
            'question': new_question.question,
            'answer': new_question.answer,
            'category': new_question.category,
            'difficulty': new_question.difficulty
        }}), 201


    """
    
    
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search_questions():
        # Get the search term from the request
        search_term = request.get_json().get('searchTerm')

        # Query the database for questions containing the search term
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        # Convert the questions to a list of dictionaries for JSON serialization
        question_list = [question.__dict__ for question in questions]

        # Remove the unnecessary attributes and return the question data
        for question in question_list:
            question.pop('_sa_instance_state', None)

        if question_list:
            return jsonify({'questions': question_list, 'success': True}) 
        else:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<string:category>/questions', methods=['GET'])
    def get_questions_by_category(category):
        # Query the database for questions in the specified category
        questions = Question.query.filter_by(category=category).all()

        # Convert the questions to a list of dictionaries for JSON serialization
        question_list = [question.__dict__ for question in questions]

        # Remove the unnecessary attributes and return the question data
        for question in question_list:
            question.pop('_sa_instance_state', None)

        return jsonify({'questions': question_list})
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        category = data.get('category', None)
        previous_questions = data.get('previous_questions', [])
        if category:
            question = Question.query.filter_by(category=category)\
                                    .filter(Question.id.notin_(previous_questions))\
                                    .order_by(func.random())\
                                    .first()
        else:
            question = Question.query.filter(Question.id.notin_(previous_questions))\
                                    .order_by(func.random())\
                                    .first()
        if question:
            return jsonify({
                'success': True,
                'question': {
                    'id': question.id,
                    'question': question.question,
                    'answer': question.answer,
                    'category': question.category
                }
            })
        else:
            return jsonify({
                'success': False
            })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # 404 Error
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    # 422 Error
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    # 500 Error
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    # Handle other expected errors here

    # Error handler for general exceptions
    @app.errorhandler(Exception)
    def handle_exception(error):
        message = str(error)
        return jsonify({
            'success': False,
            'error': 500,
            'message': message
        }), 500

    return app
    
"""     # Error handler for custom defined exceptions
    @app.errorhandler(MyCustomException)
    def handle_my_custom_exception(error):
        message = error.message
        status_code = error.status_code
        return jsonify({
            'success': False,
            'error': status_code,
            'message': message
        }), status_code

    # Error handler for HTTPException subclasses
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        message = error.description
        status_code = error.code
        return jsonify({
            'success': False,
            'error': status_code,
            'message': message
        }), status_code   
    """ 
    
  

