import os
import requests
import simplejson as json
import json
import sys
from flask import Flask, request, abort, jsonify, render_template, session, make_response, Response, flash, url_for, redirect, _request_ctx_stack, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth, check_permissions, verify_decode_jwt
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from config import SECRET_KEY
from jose import jwt
from functools import wraps
from urllib.request import urlopen
from os import environ


# AUTH0_DOMAIN = 'fsnd-ml-casting-agency.eu.auth0.com'
# ALGORITHMS = ['RS256']
# API_AUDIENCE = 'Casting'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
# class AuthError(Exception):
#     def __init__(self, error, status_code):
#         self.error = error
#         self.status_code = status_code

# AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
# AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
# AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
# AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
# AUTH0_BASE_URL = os.getenv('AUTH0_BASE_URL')
# AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
#----------------------------------------------------------------------------#
# Initialize App
#----------------------------------------------------------------------------#

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    app.secret_key = SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY
    setup_db(app)
    CORS(app)

    return app


app = create_app()


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
# auth0 info
# oauth = OAuth(app)

# auth0 = oauth.register(
#     'auth0',
#     client_id=AUTH0_CLIENT_ID,
#     client_secret=AUTH0_CLIENT_SECRET,
#     api_base_url=AUTH0_BASE_URL,
#     access_token_url='fsnd-ml-casting-agency.eu.auth0.com' + '/oauth/token',
#     authorize_url='fsnd-ml-casting-agency.eu.auth0.com' + '/authorize',
#     client_kwargs={
#         'scope': 'openid profile email'
#             }
# )

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response

# The starting point of index/homepage of the app



@app.route('/')
def index():
    return jsonify({
        'GET /actors': 'List actors',
        'GET /actors-detail': 'List actors with details',
        'POST /actors': 'Create a actor profile',
        'PATCH /actors/<id>': 'Update a actor',
        'DELETE /actors/<id>': 'Delete a actor'
    })


#  Actors
#  ----------------------------------------------------------------
# This is the handler for providing a list of actors from the database


@app.route('/actors', methods=['GET'])
@cross_origin()
@requires_auth('get:actors')
def get_actors(payload):
    actors = Actor.query.all()
    actors_data = []
    for actor in actors:
        actors_data.append({
            "id": actor.id,
            "name": actor.name,
            "age": actor.age,
            "gender": actor.gender,
            "image_link": actor.image_link
        })
        result = actors_data

    return jsonify(result)

# This is the handler for creating a actor in the database. Check on the specific right in authentication

@app.route('/actors/create', methods=['POST'])
@requires_auth('post:actors')
def create_actor(payload):
    try:
        name = request.json.get('name'),
        age = request.json.get('age'),
        gender = request.json.get('gender'),
        image_link = request.json.get('image_link'),
        newActor = Actor(name=name, age=age, gender=gender,
                         image_link=image_link)

        newActor.insert()

        return jsonify({'success': True, 'Actors': [newActor.format()]})
    except Exception:
        abort(404)


# This is the handler for getting a specific actor in the database.
@app.route('/actors/<int:actor_id>', methods=['GET'])
@requires_auth('get:actors')
def get_actor_details(payload, actor_id):
    actor = Actor.query.get(actor_id)

    if actor is None:
        return json.dumps({
            'success': False,
            'error': 'Actor could not be found'
        }), 404

    actor_details = ({
        "id": actor.id,
        "name": actor.name,
        "age": actor.age,
        "gender": actor.gender,
        "image_link": actor.image_link
    })
    return jsonify(actor_details)


# This is the handler for updating a specific actor in the database.
@app.route('/actors/<int:actor_id>/patch', methods=['GET', 'PATCH'])
@requires_auth('patch:actors')
def update_actor_form(payload, actor_id):
    actor = Actor.query.get(actor_id)

    if actor is None:
        return json.dumps({
            'success': False,
            'error': 'Actor could not be found to be updated',
        }), 404

    actor_details = ({
        "id": actor.id,
        "name": actor.name,
        "age": actor.age,
        "gender": actor.gender,
        "image_link": actor.image_link
    })
    return jsonify(actor_details)


# This is the handler for deleting a specific actor in the database.
@app.route('/actors/<int:actor_id>/delete', methods=['GET', 'DELETE'])
@requires_auth('delete:actors')
def delete_actor(payload, actor_id):
    actor = Actor.query.get(actor_id)

    if actor is None:
        return json.dumps({
            'success': False,
            'error': 'Actor could not be found to be deleted',
        }), 404

    try:
        actor.delete()
        return json.dumps({
            'success': True,
            'error': 'Actor was successfully deleted!'
        }), 200

    except:
        error = True
        flash('An error occurred. This actor could not be deleted.')
    return jsonify(error)

#  Movies
#  ----------------------------------------------------------------
# This is the handler for providing a list of movies from the database


@app.route('/movies', methods=['GET'])
@cross_origin()
@requires_auth('get:movies')
def get_movies(payload):
    movies = Movie.query.all()
    movies_data = []
    for movie in movies:
        movies_data.append({
            "id": movie.id,
            "name": movie.name,
            "genre": movie.genre,
            "release_year": movie.release_year,
            "rating": movie.rating
        })
        result = movies_data

    return jsonify(result)

# This is the handler for creating a movie in the database.


@app.route('/movies/create', methods=['POST'])
@requires_auth('post:movies')
def create_movie(payload):

    try:
        name = request.json.get('name'),
        director = request.json.get('director'),
        genre = request.json.get('genre'),
        release_year = request.json.get('release_year'),
        rating = request.json.get('rating'),
        newMovie = Movie(name=name, director=director, genre=genre,
                         release_year=release_year, rating=rating)
        newMovie.insert()
        return jsonify({'success': True, 'Movies': [newMovie.format()]})
    except Exception:
        abort(404)


# This is the handler for updating a movie from the database.
@app.route('/movies/<int:movie_id>', methods=['GET'])
@requires_auth('get:movies')
def get_movie_details(payload, movie_id):

    movie = Movie.query.get(movie_id)

    if movie is None:
        return json.dumps({
            'success': False,
            'error': 'Movie could not be found'
        }), 404

    movie_details = ({
        "id": movie.id,
        "name": movie.name,
        "director": movie.director,
        "genre": movie.genre,
        "release_year": movie.release_year,
        "rating": movie.rating
    })

    return jsonify(movie_details)

# This is the handler for updating a movie from the database.


@app.route('/movies/<int:movie_id>/patch', methods=['GET', 'PATCH'])
@requires_auth('patch:movies')
def update_movie_form(payload, movie_id):

    movie = Movie.query.get(movie_id)

    if movie is None:
        return json.dumps({
            'success': False,
            'error': 'Movie could not be found to be updated',
        }), 404

    movie_details = ({
        "id": movie.id,
        "name": movie.name,
        "director": movie.director,
        "genre": movie.genre,
        "release_year": movie.release_year,
        "rating": movie.rating
    })

    return jsonify(movie_details)


# This is the handler for deleting a movie from the database.
@app.route('/movies/<int:movie_id>/delete', methods=['GET', 'DELETE'])
@requires_auth('delete:movies')
def delete_movie(payload, movie_id):

    movie = Movie.query.get(movie_id)

    if movie is None:
        return json.dumps({
            'success': False,
            'error': 'Movie could not be found to be deleted',
        }), 404

    try:
        movie.delete()

        return json.dumps({
            'success': True,
            'error': 'Movie was successfully deleted!'
        }), 200

    except:
        error = True
        flash('An error occurred. This movie could not be deleted.')
    return jsonify(error)

# #  Cast a Movie
# #  ----------------------------------------------------------------
# # route handler to get to form to cast a movie
# @app.route('/cast/create', methods=['GET'])
# #@requires_auth('get:castform')
# #def create_cast_form(payload):
# def create_cast_form():
# 	movies = Movie.query.all()
# 	actors = Actor.query.all()

# 	return render_template('forms/new_cast.html', movies=movies, actors=actors)

# # route handler to cast a movie in db
# @app.route('/cast/create', methods=['POST'])
# #@requires_auth('post:cast')
# #def create_cast(payload):
# def create_cast():
# 	error = False
# 	actor_id = request.form.get('actor_id')
# 	movie_id = request.form.get('movie_id')

# 	try:
# 		actor = Actor.query.get(actor_id)
# 		movie = Movie.query.get(movie_id)

# 		if actor is None:
# 			return json.dumps({
# 			'success': False,
# 			'error': 'Actor could not be found'
# 			}), 404

# 		if movie is None:
# 			return json.dumps({
# 			'success': False,
# 			'error': 'Movie could not be found'
# 			}), 404

# 		movie.cast.append(actor)
# 		movie.update()

# 	except:
# 		error = True

# 	if error:
# 		flash('Error: This actor was not cast. Please check your inputs and try again :)')

# 	else:
# 		# success message upon succeesful casting
# 		flash('This actor was successfully booked!')

# 	return render_template('pages/home.html')


# Example error handling for unprocessable entity

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# Errorhandler for 500 (server error)


@app.errorhandler(500)
def inter_serv(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": error.description
    }), 500


# Errorhandler for 404 (resource not found)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# Error handler for 401 (Unauthorized)

@app.errorhandler(401)
def un_auth(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


# Error handler for AuthError (Unauthorized)

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify(ex.error), ex.status_code


if __name__ == '__main__':
    app.run()(debug=True)
    #  app.run(host='0.0.0.0', port=8080, debug=True)
