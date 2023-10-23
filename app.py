from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE_NAME = "stocks.db"

def get_db():
    return sqlite3.connect(DATABASE_NAME)

@app.route('/stocks', methods=['GET'])
def fetch_stocks():
    con = get_db()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM stocks")
    stocks = cursor.fetchall()
    con.close()

    # Transforming tuple data to JSON format
    stocks_list = [{"name": stock[0], "ticker_symbol": stock[1], "current_price": stock[2]} for stock in stocks]

    return jsonify(stocks_list)

@app.route('/stocks/add', methods=['POST'])
def add_stock():
    data = request.get_json()

    # Validate input
    if not all(key in data for key in ("name", "ticker_symbol", "current_price")):
        return jsonify({"error": "Missing data!"}), 400

    name = data["name"]
    ticker_symbol = data["ticker_symbol"]
    current_price = data["current_price"]

    con = get_db()
    cursor = con.cursor()
    try:
        cursor.execute("INSERT INTO stocks (name, ticker_symbol, current_price) VALUES (?, ?, ?)", 
                       (name, ticker_symbol, current_price))
        con.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        con.close()

    return jsonify({"success": "Stock added successfully!"})

@app.route('/update_stock/<ticker_symbol>', methods=['PUT'])
def update_stock(ticker_symbol):
    stock_data = request.get_json()

    new_price = stock_data['current_price']

    try:
        with sqlite3.connect('stocks.db') as conn:
            cursor = conn.cursor()

            # Update the stock's current price using its ticker_symbol
            cursor.execute("UPDATE stocks SET current_price = ? WHERE ticker_symbol = ?", (new_price, ticker_symbol))
            
            # Check if the stock was updated
            if cursor.rowcount == 0:
                return jsonify({"error": "No stock found with the provided ticker_symbol"}), 404

            conn.commit()

        return jsonify({"success": True, "message": "Stock updated successfully!"})

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/delete_stock/<ticker_symbol>', methods=['DELETE'])
def delete_stock(ticker_symbol):
    try:
        with sqlite3.connect('stocks.db') as conn:
            cursor = conn.cursor()

            # Delete the stock using its ticker_symbol
            cursor.execute("DELETE FROM stocks WHERE ticker_symbol = ?", (ticker_symbol, ))

            # Check if the stock was deleted
            if cursor.rowcount == 0:
                return jsonify({"error": "No stock found with the provided ticker_symbol"}), 404

            conn.commit()

        return jsonify({"success": True, "message": "Stock deleted successfully!"})

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

