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
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    
    drinks = [drink.short() for drink in all_drinks]

    return jsonify({
        "success": True, 
        "drinks": drinks
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    all_drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        "success": True, 
        "drinks": long_drinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    new_drink_info = request.get_json()

    title = new_drink_info.get('title')
    json_recipe = new_drink_info.get('recipe')

    if json_recipe is None:
        abort(422)
    try:

        new_drink = Drink(title = title, recipe = json.dumps(json_recipe))
        new_drink.insert()

        return jsonify({
            "success": True, 
            "drinks": json_recipe
        })
        
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):

    patch_drink_info = request.get_json()

    title = patch_drink_info.get('title')
    json_recipe = patch_drink_info.get('recipe')

    try:
        drink_to_patch = Drink.query.get(id)
    except:
        abort(404)

    if not drink_to_patch:
        abort(422)

    try:
        if title:
            drink_to_patch.title = title

        if json_recipe:
            drink_to_patch.recipe = json.dumps(json_recipe)

        drink_to_patch.update()

        return jsonify({
            "success": True, 
            "drinks": [drink_to_patch.long()]
        })
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink_to_delete = Drink.query.get(id)
    except:
        abort(404)
    
    try:
        drink_to_delete.delete()

        return jsonify({
            "success": True, 
            "delete": drink_to_delete.id
        })
    except:
        abort(422)

## Error Handling
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "not found"
                    }), 404

@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": ex.error
                    }), 401