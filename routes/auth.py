from flask import Blueprint, request, jsonify
from models.user import User, db
from models.tokenblacklist import TokenBlacklist
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "customer")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    if role not in ["customer", "admin"]:
        return jsonify({"message": "Invalid role"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    user = User(email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity={"id": user.id, "role": user.role}, expires_delta=timedelta(hours=1))
    refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role})

    return jsonify({
        "user": {"id": user.id, "email": user.email, "role": user.role},
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity={"id": user.id, "role": user.role}, expires_delta=timedelta(hours=1))
    refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role})

    return jsonify({
        "user": {"id": user.id, "email": user.email, "role": user.role},
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity, expires_delta=timedelta(hours=1))
    return jsonify({"access_token": new_access}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blocked_token = TokenBlacklist(jti=jti)
    db.session.add(blocked_token)
    db.session.commit()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    identity = get_jwt_identity()
    if identity["role"] != "admin":
        return jsonify({"message": "Admins only"}), 403

    users = User.query.all()
    users_list = [
        {"id": u.id, "email": u.email, "role": u.role, "created_at": u.created_at.isoformat()}
    ]
    return jsonify({"users": users_list}), 200
