from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/notify/log', methods=['POST'])
def log_event():
    data = request.get_json()
    print(f"LOG RECIBIDO: {data}") # Esto se verá en tu terminal de Flask
    return jsonify({"status": "Log ok"}), 201

if __name__ == '__main__':
    app.run(port=5000)