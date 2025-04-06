from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_cors import CORS
from db import DatabaseDriver
from ml_model import train_model, predict_category, evaluate_model
from plaid_api import get_transactions

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'my_secret_key'
jwt = JWTManager(app)
CORS(app)

db = DatabaseDriver()

# ----------------- AUTHENTICATION -----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]
    
    try:
        db.register_user(username, password)
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]
    
    user_id = db.login_user(username, password)
    if user_id:
        access_token = create_access_token(identity=user_id)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# ----------------- TRANSACTIONS -----------------
@app.route("/transactions", methods=["POST"])
@jwt_required()
def add_transaction():
    data = request.json
    user_id = data["user_id"]
    amount = data["amount"]
    category = data["category"]
    description = data.get("description", "")

    db.add_transaction(user_id, amount, category, description)
    return jsonify({"message": "Transaction added successfully!"}), 201

@app.route("/transactions/<int:user_id>", methods=["GET"])
@jwt_required()
@app.route("/fetch_transactions", methods=["POST"])
def fetch_transactions():
    data = request.json
    access_token = data.get("access_token")
    
    if not access_token:
        return jsonify({"error": "Missing access token"}), 400
    
    transactions = get_transactions(access_token)
    return jsonify(transactions)

@app.route("/transactions/delete/<int:transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id):
    db.delete_transaction(transaction_id)
    return jsonify({"message": "Transaction deleted successfully!"}), 200

# ----------------- BUDGETS -----------------
@app.route("/budget", methods=["POST"])
@jwt_required()
def set_budget():
    data = request.json
    user_id = data["user_id"]
    category = data["category"]
    limit_amount = data["limit_amount"]

    db.set_budget(user_id, category, limit_amount)
    return jsonify({"message": "Budget set successfully!"}), 201

@app.route("/budget/check", methods=["POST"])
@jwt_required()
def check_budget():
    data = request.json
    user_id = data["user_id"]
    category = data["category"]

    exceeded = db.check_budget_exceeded(user_id, category)
    return jsonify({"budget_exceeded": exceeded}), 200

# ----------------- RECEIPTS -----------------
@app.route("/receipt/upload", methods=["POST"])
@jwt_required()
def upload_receipt():
    data = request.json
    user_id = data["user_id"]
    transaction_id = data["transaction_id"]
    file_path = data["file_path"]

    db.store_receipt(user_id, transaction_id, file_path)
    return jsonify({"message": "Receipt stored successfully!"}), 201

@app.route("/receipt/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_receipt(transaction_id):
    receipt_path = db.get_receipt(transaction_id)
    if receipt_path:
        return jsonify({"receipt_path": receipt_path}), 200
    return jsonify({"error": "Receipt not found"}), 404

# ----------------- MACHINE LEARNING -----------------
@app.route("/train_model", methods=["POST"])
@jwt_required()
def train():
    train_model()
    return jsonify({"message": "Model trained successfully!"}), 200

@app.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    data = request.json
    amount = data["amount"]
    description = data.get("description", "")

    category = predict_category(amount, description)
    return jsonify({"category": category}), 200

@app.route("/evaluate", methods=["GET"])
@jwt_required()
def evaluate():
    evaluate_model()
    return jsonify({"message": "Model evaluation completed!"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
