#export API_KEY=pk_148005baa9384f6384f85bc628c94f63

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash[0]["cash"]

    #symbol price  shares total_price

    symbols = db.execute("SELECT symbol FROM stocks WHERE id = ?", session["user_id"])

    print(symbols)
    slist = []
    for s in symbols:
        slist += [s["symbol"]]
    print(slist)
    #return redirect("/")

    return render_template("index.html", cash = cash)
    """Show portfolio of stocks"""
    #return apology("TODO")



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = lookup(request.form.get("symbol"))
        if symbol == None:
            return apology("symbol not found", 403)


        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = cash[0]["cash"]
        #print("cash ", cash, "session[user_id] ", session["user_id"])

        price = symbol["price"]

        shares = request.form.get("shares")

        if not shares:
            return apology("please input shares", 403)
        else:
            shares = int(shares)

        total = shares * price

        if total > cash:
            return apology("you can't afford that", 403)

        cash -= total
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        amount = db.execute("SELECT amount FROM stocks WHERE id = ? AND symbol = ?", session["user_id"], symbol["symbol"])
        if not amount:
            db.execute("INSERT INTO stocks (id, symbol, amount) VALUES (?, ?, ?)", session["user_id"], symbol["symbol"], shares)
        else:
            db.execute("UPDATE stocks SET amount = ? WHERE id = ? AND symbol = ?", int(amount[0]["amount"]) + shares, session["user_id"], symbol["symbol"])
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("please input symbol", 403)
        else:
            symbol = lookup(request.form.get("symbol"))
            #print(symbol)
            if symbol == None:
                return apology("symbol not found", 403)
            return render_template("quoted.html", symbol = symbol)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("please input username", 403)

        elif not request.form.get("password"):
            return apology("please input password", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 403)

        users = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(users) != 0:
            return apology("username already exists")


        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        return redirect("/")
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
