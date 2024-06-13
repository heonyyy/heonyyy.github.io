import os
from flask import Flask, session
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User, UserImage
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwer1234@localhost:5433/myDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dkssudgktpdy'

CORS(app, resources={r"/*": {"origins": "http://localhost:3000", "supports_credentials": True}})
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.permanent_session_lifetime = datetime.timedelta(days=1)

# 이미지 저장 디렉토리 경로 설정
image_dir = r'images'
os.makedirs(image_dir, exist_ok=True)
app.config['IMAGE_DIR'] = image_dir

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# auth 모듈과 image_processing 모듈 가져오기
from auth import login, logout, register
from image_processing import process_text
app.register_blueprint(login)
app.register_blueprint(logout)
app.register_blueprint(register)
app.register_blueprint(process_text)

if __name__ == '__main__':
    app.run(debug=True)