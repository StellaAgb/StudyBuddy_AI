from flask import Flask, jsonify, render_template, request
from agent import run_study_agent

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/api/plan')
def plan():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(run_study_agent(data.get('tasks', []), data.get('available_hours', 3)))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

if __name__ == '__main__':
    app.run(debug=True)
