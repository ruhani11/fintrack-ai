from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from utils import generate_budget_tip

app = Flask(__name__)
CORS(app)

DB_FILE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions")
    rows = cur.fetchall()
    conn.close()
    transactions = [dict(row) for row in rows]
    return jsonify(transactions)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()
        amount = float(data.get('amount'))
        category = data.get('category')
        date = data.get('date')
        month = data.get('month')

        if not all([amount, category, date, month]):
            return jsonify({"error": "Missing fields"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (amount, category, date, month) VALUES (?, ?, ?, ?)",
                    (amount, category, date, month))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Transaction added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/summary', methods=['POST'])
def get_summary():
    data = request.get_json()
    month = data.get('month')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) as total FROM transactions WHERE month = ? GROUP BY category", (month,))
    rows = cur.fetchall()
    conn.close()

    summary = {row['category']: row['total'] for row in rows}
    return jsonify(summary)

@app.route('/api/tip', methods=['POST'])
def get_tip():
    data = request.get_json()
    summary = data.get('summary')
    income = data.get('income')

    if not summary or income is None:
        return jsonify({'tip': '💡 Please provide both expense summary and monthly income.'}), 400

    tip = generate_budget_tip(summary, income)
    return jsonify({'tip': tip})

if __name__ == '__main__':
    app.run(debug=True)
