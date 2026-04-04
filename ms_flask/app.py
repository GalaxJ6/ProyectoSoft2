from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

def make_log(event, user_id, details=None, status='SUCCESS'):
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "user_id": user_id,
        "details": details,
        "status": status
    }
    print(f"[LOG EVENT]: {entry}")
    return entry


@app.route('/api/notify/log', methods=['POST'])
def log_event():
    data = request.get_json()

    if not data or 'event' not in data or 'user_id' not in data:
        return jsonify({"error": "Faltan datos obligatorios para el log"}), 400

    details = data.get('details') or data.get('product') or 'N/A'
    log_entry = make_log(data['event'], data['user_id'], details)

    return jsonify({
        "message": "Log registrado exitosamente en Flask",
        "log": log_entry
    }), 201


@app.route('/api/notify/login', methods=['POST'])
def log_login():
    data = request.get_json()
    if not data or 'user_id' not in data or 'username' not in data:
        return jsonify({"error": "Faltan datos obligatorios para login"}), 400

    log_entry = make_log('login', data['user_id'], f"username={data['username']}")

    return jsonify({"message": "Login log creado", "log": log_entry}), 201


@app.route('/api/notify/logout', methods=['POST'])
def log_logout():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Faltan datos obligatorios para logout"}), 400

    log_entry = make_log('logout', data['user_id'])

    return jsonify({"message": "Logout log creado", "log": log_entry}), 201


@app.route('/api/notify/recovery', methods=['POST'])
def log_recovery():
    data = request.get_json()
    if not data or 'user_id' not in data or 'email' not in data:
        return jsonify({"error": "Faltan datos obligatorios para recovery"}), 400

    log_entry = make_log('password_recovery', data['user_id'], f"email={data['email']}")

    return jsonify({"message": "Recovery log creado", "log": log_entry}), 201


@app.route('/api/notify/user-data', methods=['POST'])
def log_user_data():
    data = request.get_json()
    if not data or 'user_id' not in data or 'action' not in data:
        return jsonify({"error": "Faltan datos obligatorios para user-data"}), 400

    details = f"action={data['action']}"
    if 'fields' in data:
        details += f",fields={data['fields']}"

    log_entry = make_log('user_data', data['user_id'], details)

    return jsonify({"message": "User-data log creado", "log": log_entry}), 201


@app.route('/api/notify/products', methods=['POST'])
def log_products():
    data = request.get_json() or {}
    user_id = data.get('user_id', 'anon')
    action = data.get('action', 'view')

    details = f"action={action}, query={data.get('query', 'all')}"
    log_entry = make_log('products_' + action, user_id, details)

    return jsonify({"message": "Products log creado", "log": log_entry}), 201


@app.route('/api/notify/event', methods=['POST'])
def log_generic_event():
    data = request.get_json()
    if not data or 'event' not in data or 'user_id' not in data:
        return jsonify({"error": "Faltan datos obligatorios para event"}), 400

    details = data.get('details', 'N/A')
    log_entry = make_log(data['event'], data['user_id'], details)

    return jsonify({"message": "Evento genérico log creado", "log": log_entry}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5000)
