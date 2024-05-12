from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import *
from datetime import datetime
import hashlib as hl

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost/flask'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(VARCHAR(50), unique=True, nullable=False)
    password = db.Column(VARCHAR(100), nullable=False)
    registration_date = db.Column(TIMESTAMP, nullable=False, default=datetime.now)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/user/', methods=['GET'])
def register_user():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        data = request.get_json()
        login = data.get('login')
        password = data.get('password')
        if not login or not password:
            return jsonify({'error': 'Missing login or password'}), 400
        
        # Проверяем уникальность логина
        if User.query.filter_by(login=login).first():
            return jsonify({'error': 'Login already exists'}), 400
        
        # Хешируем пароль с солью и добавляем пользователя в базу данных
        hashed_password = hl.sha3_256((password + login[:2] + login[-1]).encode('utf-8')).hexdigest()
        new_user = User(login=login, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return render_template('registration.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)