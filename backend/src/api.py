import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# Get drinks
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # Get all drinks
    drinks = Drink.query.all()
    # Check if there are no drinks
    if len(drinks) == 0:
        abort(404)
    # Format drinks
    formatted_drinks = [drink.short() for drink in drinks]
    # Return drinks
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# Get drinks detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    # Get all drinks
    drinks = Drink.query.all()
    # Check if there are no drinks
    if len(drinks) == 0:
        abort(404)
    # Format drinks
    formatted_drinks = [drink.long() for drink in drinks]
    # Return drinks
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

# Create drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    # Get request body
    body = request.get_json()
    # Get title and recipe from body
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    # Check if title or recipe is empty
    if title is None or recipe is None:
        abort(422)
    # Create new drink
    drink = Drink(title=title, recipe=json.dumps(recipe))
    # Insert new drink
    drink.insert()
    # Return new drink
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

# Update drink
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    # Get drink by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # Check if drink exists
    if drink is None:
        abort(404)
    # Get request body
    body = request.get_json()
    # Get title and recipe from body
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    # Check if title or recipe is empty
    if title is None or recipe is None:
        abort(422)
    # Update drink
    drink.title = title
    drink.recipe = json.dumps(recipe)
    # Update drink
    drink.update()
    # Return updated drink
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

# Delete drink
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # Get drink by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # Check if drink exists
    if drink is None:
        abort(404)
    # Delete drink
    drink.delete()
    # Return deleted drink id
    return jsonify({
        'success': True,
        'delete': id
    }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def not_found(error):
    # Return error 404
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

# Error handler for AuthError
@app.errorhandler(AuthError)
def auth_error(error):
    # Return error 401
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    }), 401

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

# Error handler for 401
@app.errorhandler(401)
def unauthorized(error):
    # Return error 401
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    }), 401
