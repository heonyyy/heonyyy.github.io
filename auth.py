# auth.py
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required
from models import User, db

login = Blueprint('login', __name__)
logout = Blueprint('logout', __name__)
register = Blueprint('register', __name__)

# 로그인
@login.route('/login', methods=['POST'])
def login_route():
    data = request.json
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# 로그인 확인
@login.route('/check-login')
def check_login():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({'message': 'User is logged in', 'user': user.username})
    return jsonify({'message': 'User is not logged in'}), 401

# 로그아웃
@logout.route('/logout', methods=['POST'])
@login_required
def logout_route():
    logout_user()
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

# 신규 등록자
@register.route('/register', methods=['POST'])
def register_route():
    data = request.json
    username = data['username']
    password = data['password']
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'})