from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('stock_id', db.Integer, db.ForeignKey('stock.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    stocks = db.relationship('Stock', secondary=watchlist, backref=db.backref('users', lazy='dynamic'))

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Uncomment below to use old SQLite database setup
# DATABASE_NAME = "stocks.db"
# def get_db():
#     return sqlite3.connect(DATABASE_NAME)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@app.route('/stocks', methods=['GET'])
def fetch_stocks():
    stocks = Stock.query.all()
    stocks_list = [{"name": stock.ticker, "ticker_symbol": stock.ticker, "current_price": stock.price} for stock in stocks]
    return jsonify(stocks_list)

    # Uncomment below to use old SQLite database setup
    # con = get_db()
    # cursor = con.cursor()
    # cursor.execute("SELECT * FROM stocks")
    # stocks = cursor.fetchall()
    # con.close()
    # stocks_list = [{"name": stock[0], "ticker_symbol": stock[1], "current_price": stock[2]} for stock in stocks]
    # return jsonify(stocks_list)

@app.route('/stocks/add', methods=['POST'])
def add_stock():
    data = request.get_json()
    new_stock = Stock(ticker=data['ticker_symbol'], price=data['current_price'])
    db.session.add(new_stock)
    db.session.commit()
    return jsonify({"success": "Stock added successfully!"})

    # Uncomment below to use old SQLite database setup
    # name = data["name"]
    # ticker_symbol = data["ticker_symbol"]
    # current_price = data["current_price"]
    # con = get_db()
    # cursor = con.cursor()
    # try:
    #     cursor.execute("INSERT INTO stocks (name, ticker_symbol, current_price) VALUES (?, ?, ?)", 
    #                    (name, ticker_symbol, current_price))
    #     con.commit()
    # except sqlite3.Error as e:
    #     return jsonify({"error": f"Database error: {e}"}), 500
    # finally:
    #     con.close()

@app.route('/update_stock/<ticker_symbol>', methods=['PUT'])
def update_stock(ticker_symbol):
    stock_data = request.get_json()
    stock = Stock.query.filter_by(ticker=ticker_symbol).first()
    stock.price = stock_data['current_price']
    db.session.commit()
    updated_stock_data = {
        "ticker_symbol": ticker_symbol,
        "current_price": stock_data['current_price']
    }
    socketio.emit('stock_update', updated_stock_data)
    return jsonify({"success": True, "message": "Stock updated successfully!"})

    # Uncomment below to use old SQLite database setup
    # new_price = stock_data['current_price']
    # try:
    #     with sqlite3.connect('stocks.db') as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("UPDATE stocks SET current_price = ? WHERE ticker_symbol = ?", (new_price, ticker_symbol))
    #         if cursor.rowcount == 0:
    #             return jsonify({"error": "No stock found with the provided ticker_symbol"}), 404
    #         conn.commit()
    #     updated_stock_data = {
    #         "ticker_symbol": ticker_symbol,
    #         "current_price": stock_data['current_price']
    #     }
    #     socketio.emit('stock_update', updated_stock_data)
    #     return jsonify({"success": True, "message": "Stock updated successfully!"})
    # except Exception as e:
    #     return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/delete_stock/<ticker_symbol>', methods=['DELETE'])
def delete_stock(ticker_symbol):
    stock = Stock.query.filter_by(ticker=ticker_symbol).first()
    db.session.delete(stock)
    db.session.commit()
    return jsonify({"success": True, "message": "Stock deleted successfully!"})

    # Uncomment below to use old SQLite database setup
    # try:
    #     with sqlite3.connect('stocks.db') as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("DELETE FROM stocks WHERE ticker_symbol = ?", (ticker_symbol, ))
    #         if cursor.rowcount == 0:
    #             return jsonify({"error": "No stock found with the provided ticker_symbol"}), 404
    #         conn.commit()
    #     return jsonify({"success": True, "message": "Stock deleted successfully!"})
    # except Exception as e:
    #     return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists!"
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return "User created successfully!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            return "Username not found!"
        login_user(user)
        return "Logged in successfully!"
    return render_template('login.html')

@app.route('/watchlist/add/<ticker_symbol>', methods=['POST'])
@login_required
def add_to_watchlist(ticker_symbol):
    stock = Stock.query.filter_by(ticker=ticker_symbol).first()
    if not stock:
        return "Stock not found!"
    current_user.stocks.append(stock)
    db.session.commit()
    return "Stock added to watchlist!"

@app.route('/watchlist', methods=['GET'])
@login_required
def view_watchlist():
    user_stocks = current_user.stocks.all()
    # Convert the list of Stock objects to your preferred format and return

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    socketio.run(app, debug=True)
