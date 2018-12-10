
from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, make_response, json

import config
from models import User, Pet
from exts import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})


@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})


@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):

    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@app.route('/user/promote/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'The user has been promoted'})


@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def update_user(current_user, public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    new_name = json.loads(request.data)
    user.name = new_name.get('name')
    db.session.commit()

    return jsonify({'message' : 'The user has been updated'})


@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW.Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW.Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})


@app.route('/pet', methods=['GET'])
@token_required
def get_all_pets(current_user):
    pets = Pet.query.filter_by(owner_id=current_user.id).all()

    output = []

    for pet in pets:
        pet_data = {}
        pet_data['id'] = pet.id
        pet_data['name'] = pet.name

        output.append(pet_data)
    return jsonify({'pets' : output})


@app.route('/pet/<pet_id>', methods=['GET'])
@token_required
def get_one_pet(current_user, pet_id):
    pet = Pet.query.filter_by(id=pet_id, owner_id=current_user.id).first()

    if not pet:
        return jsonify({'message': "No Pet found"})

    pet_data = {}
    pet_data['id'] = pet.id
    pet_data['name'] = pet.name
    return jsonify(pet_data)


@app.route('/pet', methods=['POST'])
@token_required
def create_pet(current_user):
    data = request.get_json()

    new_pet = Pet(name=data['name'], owner_id=current_user.id)
    db.session.add(new_pet)
    db.session.commit()
    return jsonify({'message': "Pet created!"})


@app.route('/pet/<pet_id>', methods=['PUT'])
@token_required
def update_pet(current_user, pet_id):
    pet = Pet.query.filter_by(id=pet_id, owner_id=current_user.id).first()
    if not pet:
        return jsonify({'message': "No Pet found"})

    new_name = json.loads(request.data)
    pet.name = new_name.get('name')

    db.session.commit()

    return jsonify({'message': 'Pet updated!'})


@app.route('/pet/<pet_id>', methods=['DELETE'])
@token_required
def delete_pet(current_user, pet_id):
    pet = Pet.query.filter_by(id=pet_id, owner_id=current_user.id).first()
    if not pet:
        return jsonify({'message': "No Pet found"})

    db.session.delete(pet)
    db.session.commit()

    return jsonify({'message': "Pet deleted!"})


if __name__ == '__main__':
    app.run(debug=True)
