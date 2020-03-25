import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json 
import sys

from models import setup_db, Question, Category

db = SQLAlchemy()

QUESTIONS_PER_PAGE = 10

# paginating questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    # Set up CORS with '*' for origins
    CORS(app, resources={'/': {'origins': '*'}})

    # CORS headers to set access control
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response


    # -------------------------------------------------------------------------------------
    # GET requests
    # -------------------------------------------------------------------------------------

    @app.route('/categories')
    def get_categories():
        # handles GET requests for all categories
        # get all categories and add to dict
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        
        #abort if no categories
        if (len(categories_dict) == 0):
            abort(404)

        #return category data to view
        return jsonify({
            'success': True,
            'categories': categories_dict
        })


    @app.route('/questions')
    def get_questions():
        #get questions and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)
        
        # abort if no questions
        if (len(current_questions) == 0):
            abort(404) 
        
        try:
            # get categories, add to dict
            categories = Category.query.all()
            categories_dict = {}
            for category in categories:
                categories_dict[category.id] = category.type

            #return all required data to view
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': categories_dict
            })
        except:
            db.session.rollback()
            print(sys.exc_info())
            abort(422)
        finally:
            db.session.close()
    


    #-----------------------------------------------------------
    # DELETE question
    #-----------------------------------------------------------

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            # get question by id, use one_or_none to only turn one result or call exception if none selected
            question = Question.query.filter_by(id=id).one_or_none()

            # abort if question not found
            if question is None:
                abort(404)
            
            # delete and return success message 
            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })
        except:
            #abort if there's a problem deleting the question 
            abort(422)
            
    #-----------------------------------------------------------
    # Create question with POST
    #-----------------------------------------------------------
    '''
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        # load request body and data
        body = request.get_json()
        
        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        # ensure all fields are filled
        if ((new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None)):
            flash("Make sure all fields are filled")
            abort(422)

        try:
            # Create and insert new question
            question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            question.insert()

            #get all questions and paginate
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    #-----------------------------------------------------------
    # Search questions
    #-----------------------------------------------------------
    '''
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Get user input
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        # apply filter for question string and check if there are results
        try: 
            # selection = db.session.query(Question).filter(Question.question.ilike('%{}%'.format(data['searchTerm']))).all()
            
            # if (len(selection) == 0):
            #     abort(404)
            # if search_term:
            #     selection = Question.query.filter(Question.question.ilike('%{}%'.format(data['searchTerm']))).all()
            #paginate and return results 
            if search_term:
                selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions':  [question.format() for question in search_results],
                'total_questions': len(selection),
                'current_category': Question.category
            })
        except:
            abort(404)

    #-----------------------------------------------------------
    # GET questions based on category
    #-----------------------------------------------------------
    '''
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:id>/questions')
    def get_category_questions(id):
        # Get category by id, try get questions from matching category
        category = Category.query.filter_by(id=id).one_or_none()
        
        try: 
            #get questions matching the category
            selection = Question.query.filter_by(category=category.id).all()

            #paginate selected questions and return results
            paginated = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all()),
                'current_category': category.type
            })
        except:
            abort(400)

    #-----------------------------------------------------------
    # Quiz play using POST
    #-----------------------------------------------------------
    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            body = request.get_json()

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            # If 'ALL' categories is 'clicked', filter available Qs 
            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            # Filter available questions by chosen category and unused questions
            else:
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((previous_questions))).all()

            # randomly select next question from available questions
            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)
        
    

#-----------------------------------------------------------
# Error Handlers
#-----------------------------------------------------------

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }),400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }),404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }),422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }),422


    return app

        