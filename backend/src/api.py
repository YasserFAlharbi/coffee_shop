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

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        if not drinks:
            abort(500)
        short = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': short
        }), 200
    except:
        abort(500)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()
        if not drinks:
            abort(500)
        Long = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': Long
        }), 200
    except:
        abort(500)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(token):
    if request.get_json():
        try:
            data = request.get_json()
            drink = Drink(
                title=data['title'],
                recipe=json.dumps(data['recipe'])
            )
            drink.insert()
            return jsonify([{
                'success': True,
                'drinks': drink.long()
            }]), 200
        except:
            abort(501)
    else:
        abort(502)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(token, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        try:
            if request.get_json():
                data = request.get_json()
                if 'title' in data:
                    drink.title = data['title']
                if 'recipe' in data:
                    drink.recipe = json.dumps(data['recipe'])
                drink.update()
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                }), 200
        except:
            abort(503)
    except:
        abort(404)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        try:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': id
            }), 200
        except:
            abort(504)
    except:
        abort(404)


# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'not getting data'
    }), 500


@app.errorhandler(501)
def create_error(error):
    return jsonify({
        'success': False,
        'error': 501,
        'message': 'error while creating the drink'
    }), 501


@app.errorhandler(502)
def miss_data(error):
    return jsonify({
        'success': False,
        'error': 502,
        'message': 'not enough data'
    }), 502


@app.errorhandler(503)
def update_error(error):
    return jsonify({
        'success': False,
        'error': 503,
        'message': 'error while updating the drink'
    }), 503


@app.errorhandler(504)
def delete_error(error):
    return jsonify({
        'success': False,
        'error': 504,
        'message': 'error while deleteing the drink'
    }), 504


@app.errorhandler(404)
def bad_id(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(error.error), error.status_code
