from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
import os
from video_text import transcribe_youtube_with_groq

os.system("> which ffmpeg ffprobe")
os.system("/usr/bin/ffmpeg")
os.system("/usr/bin/ffprobe")

app = Flask(__name__, template_folder='templates')

# ✅ Config
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vkn:LJI8O5ruUzgN4BIbFKZKTP0vgG8p6E9r@dpg-d1j1r72dbo4c73c0umlg-a.oregon-postgres.render.com/metric_team'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


# ✅ Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    chats = db.relationship('Chat', backref='user', lazy=True)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)  # ✅ now supports long text
    answer = db.Column(db.Text)    # ✅ now supports long text
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ✅ Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print(f"Token error: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# ✅ Serve HTML
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input!'}), 400

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Username already exists!'}), 409

    new_user = User(
        public_id=str(uuid.uuid4()),
        username=data['username'],
        password=data['password']  # ⚠️ plain text (not secure!)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created!'})

# ✅ Login
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth['username'] or not auth['password']:
        return make_response('Could not verify', 401)

    user = User.query.filter_by(username=auth['username']).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    if user.password == auth['password']:  # ⚠️ plain text check
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'message': 'Wrong credentials!'}), 401

# ✅ Chat
@app.route('/chat', methods=['GET', 'POST'])
@token_required
def chat(current_user):
    if request.method == 'POST':
        data = request.get_json()
        answer = transcribe_youtube_with_groq(data['question'])

        new_chat = Chat(
            question=data['question'],
            answer=answer,
            user_id=current_user.id
        )
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({'answer': answer})

    elif request.method == 'GET':
        chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.desc()).all()
        output = []
        for chat in chats:
            output.append({
                'id': chat.id,
                'question': chat.question,
                'answer': chat.answer,
                'timestamp': chat.timestamp.isoformat()
            })
        return jsonify({'chats': output})

# ✅ Route to drop & recreate the Chat table (optional, for dev only)
@app.route('/reset_chat_table', methods=['POST'])
def reset_chat_table():
    try:
        Chat.__table__.drop(db.engine)
        Chat.__table__.create(db.engine)
        return jsonify({'message': 'Chat table dropped and recreated!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Init DB & run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
