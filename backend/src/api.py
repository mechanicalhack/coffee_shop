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
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    # print("all drinks: ")
    drinks = [drink.short() for drink in all_drinks]
    print(drinks)
    # drinks = []
    # for drink in all_drinks:
    #     drinks.append({
    #         'title': drink.title,
    #         'recipe': drink.recipe.short()
    #     })

    # shortened_drinks = [drink['recipe'].short() for drink in drinks]
    return jsonify({
        "success": True, 
        "drinks": drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
# @requires_auth('get:drinks-detail')
def get_drink_details():
    all_drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        "success": True, 
        "drinks": long_drinks
    })
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
# @requires_auth('post:drinks')
def add_drink():
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
@app.route('/drinks/<int:id>', methods=['PATCH'])
def patch_drink(id):

    patch_drink_info = request.get_json()

    title = patch_drink_info.get('title')
    json_recipe = patch_drink_info.get('recipe')

    try:
        drink_to_patch = Drink.query.get(id)
    except:
        abort(404)

    try:
        if(title):
            drink_to_patch.title = title
        
        if(json_recipe):
            drink_to_patch.recipe = json.dumps(json_recipe)
        
        drink_to_patch.update()

        return jsonify({
            "success": True, 
            "delete": drink_to_patch
        })
    except:
        abort(422)

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
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink(id):
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

# @app.errorhandler(AuthError)
# def auth_error(error):
#     return jsonify({
#                     "success": False, 
#                     "error": AuthError,
#                     "message": "Authentication Error"
#                     }), 401