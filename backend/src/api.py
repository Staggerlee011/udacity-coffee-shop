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

"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
"""
# db_drop_and_create_all()

# ROUTES


# Get drinks
@app.route("/drinks", methods=["GET"])
def get_drinks():
    # Get all drinks
    drinks = Drink.query.all()
    # Check if there are no drinks
    if len(drinks) == 0:
        abort(404)
    # Format drinks
    formatted_drinks = [drink.short() for drink in drinks]
    # Return drinks
    return jsonify({"success": True, "drinks": formatted_drinks}), 200


# Get drinks detail
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    # Get all drinks
    drinks = Drink.query.all()
    # Check if there are no drinks
    if len(drinks) == 0:
        abort(404)
    # Format drinks
    formatted_drinks = [drink.long() for drink in drinks]
    # Return drinks
    return jsonify({"success": True, "drinks": formatted_drinks}), 200


# Create drink
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):
    # Get request body
    body = request.get_json()
    # Get title and recipe from body
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    # Check if title or recipe is empty
    if title is None or recipe is None:
        abort(422)
    # Create new drink
    drink = Drink(title=title, recipe=json.dumps(recipe))
    # Insert new drink
    drink.insert()
    # Return new drink
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


# Update drink
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):
    # Get drink by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # Check if drink exists
    if drink is None:
        abort(404)
    # Get request body
    body = request.get_json()
    # Get title and recipe from body
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    # Check if title or recipe is empty
    if title is None or recipe is None:
        abort(422)
    # Update drink
    drink.title = title
    drink.recipe = json.dumps(recipe)
    # Update drink
    drink.update()
    # Return updated drink
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


# Delete drink
@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    # Get drink by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # Check if drink exists
    if drink is None:
        abort(404)
    # Delete drink
    drink.delete()
    # Return deleted drink id
    return jsonify({"success": True, "delete": id}), 200


# Error Handling 422, 404, 401
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


@app.errorhandler(404)
def not_found(error):
    # Return error 404
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


# Error handler for AuthError
@app.errorhandler(AuthError)
def auth_error(error):
    # Return error 401
    return jsonify({"success": False, "error": 401, "message": "unauthorized"}), 401


# Error handler for 401
@app.errorhandler(401)
def unauthorized(error):
    # Return error 401
    return jsonify({"success": False, "error": 401, "message": "unauthorized"}), 401
