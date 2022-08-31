from flask import Flask, render_template, redirect, request, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
import json
import requests

app = Flask(__name__)
app.secret_key = "suspicious"

# Connection To Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

# Database class
# Books
class Book(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100), nullable=False)
    book_code = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f" {self.sno} - {self.book_name} - {self.book_code} - {self.author_name} - {self.availability} - {self.pub_date} - {self.datetime}"

# Issue Details
class BorrowBook(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100), nullable=False)
    book_code = db.Column(db.String(100), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_class = db.Column(db.String(100), nullable=False)
    admition_no = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.String(100), default=date.today, nullable=False)
    return_date = db.Column(db.String(100), nullable=False)
    returning_date = db.Column(db.String(100), nullable=True)
    returned = db.Column(db.String(100), default="0", nullable=True)
    datetime = db.Column(db.String(100), default=datetime.now, nullable=False)

    def __repr__(self):
        return f" {self.sno} - {self.book_name} - {self.book_code} - {self.student_name} - {self.admition_no} - {self.issue_date} - {self.return_date} - {self.returning_date} - {self.returned} - {self.datetime} "


# config.json file
with open("config.json", "r") as c:
    params = json.load(c)["params"]

# require data passing
impdata = {
    "website_name": params["websiteName"],
    "logo": params["logo"],
}

# Home Routs
@app.route("/", methods=["GET", "POST"])
def index():
    flash("welcome to "+ impdata["website_name"] +" A Library Management System.", "info")
    return render_template("index.html", impData=impdata)

# About
@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html", impData=impdata)


# Dashboard Routs
# Sigin user
@app.route("/signin", methods=["GET", "POST"])
def signIn():
    if "logdin" in session and session["logdin"]:
        flash("no need to login, You were alredy logdin.", 'success')
        return redirect("/dashboard")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == params["username"] and password == params["password"]:
            session["logdin"] = True
            flash("User logdin successfully. Now You Can Manage Library", 'success')
            return redirect("/dashboard")
    flash("Login first to use the dashboard.", 'info')
    return render_template("admin/signin.html", impData=impdata)

# signout user
@app.route("/logout", methods=["GET", "POST"])
def logoutusr():
    if "logdin" in session and session["logdin"]:
        session.pop("logdin")
    return redirect("/signin")

# Main dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def manageLibrary():
    if "logdin" in session and session["logdin"]:
        logdin = True
        Books = Book.query.all()

        return render_template(
            "admin/dashboard.html",
            impData=impdata,
            logdin=logdin,
            books=Books,
            home=True,
        )

    return redirect("/signin")


# Book Routs #
# view books
@app.route("/dashboard/viewbook", methods=["GET", "POST"])
def viewbook():
    if "logdin" in session and session["logdin"]:
        logdin = True
        Books = Book.query.all()
        return render_template(
            "admin/dashboard/viewbook.html", impData=impdata, books=Books, logdin=logdin
        )

    return redirect("/signin")

# add books
@app.route("/dashboard/addbook", methods=["GET", "POST"])
def addbook():
    if "logdin" in session and session["logdin"]:
        logdin = True
        if request.method == "POST":
            try:
                book_name = request.form.get("book_name")
                book_code = request.form.get("book_code")
                author_name = request.form.get("author_name")
                publish_date = request.form.get("publish_date")
                if book_name != "" and book_code != "" and author_name != "" and publish_date != "":
                    book = Book(
                        book_name=book_name,
                        book_code=book_code,
                        author_name=author_name,
                        pub_date=publish_date,
                        availability=True,
                        datetime=datetime.now(),
                    )

                    db.session.add(book)
                    db.session.commit()

                    flash('Book added in the library succesfully.', 'success' )
                    return redirect("/dashboard/viewbook")
                else:
                    flash('First fill all details of the book.', 'danger' )
            except Exception as e:
                flash('Book is not added to library. Internal Server Error.', 'danger' )

        return render_template(
            "admin/dashboard/addbook.html", impData=impdata, logdin=logdin
        )

    return redirect("/signin")

# edit books
@app.route("/dashboard/editbook/<string:sno>", methods=["GET", "POST"])
def editbook(sno):
    if "logdin" in session and session["logdin"]:
        logdin = True
        book = Book.query.filter_by(sno=sno).first()
        if request.method == "POST":
            try:
                book.book_name = request.form.get("book_name")
                book.book_code = request.form.get("book_code")
                book.author_name = request.form.get("author_name")
                book.pub_date = request.form.get("publish_date")
                av = request.form.get("availability")
                
                if av == "True":
                    book.availability = True
                elif av == "False":
                    book.availability = False
                db.session.commit()
                flash("succesfully updated information of the book.", "success")
            except Exception as e:
                flash("cant edit book now. Internal Server Error", "danger")

            return redirect("/dashboard")

        return render_template(
            "admin/dashboard/editbook.html", impData=impdata, book=book, logdin=logdin
        )

    return redirect("/signin")

# delete books
@app.route("/dashboard/deletebook/<string:sno>", methods=["GET", "POST"])
def deletebook(sno):
    if "logdin" in session and session["logdin"]:
        logdin = True
        try:
            sno = sno
            book = Book.query.filter_by(sno=sno).first()
            db.session.delete(book)
            db.session.commit()

            flash("successfully removed the book from library.", "success")
        except Exception as e:
            flash("can't remove this book. Book is remain in library.", "danger")

        return redirect("/dashboard/viewbook")

    return redirect("/signin")


# Borrow Book Routs #
# borrow book
@app.route("/dashboard/issuebook", methods=["GET", "POST"])
def issuebook():
    if "logdin" in session and session["logdin"]:
        if request.method == "POST":
            # search the book
            try:
                response = json.dumps(request.get_json())
                searchBook = json.loads(response)["searchbook"]
            except Exception as e:
                searchBook = False
            if searchBook:
                response = json.dumps(request.get_json())
                book_code = json.loads(response)["book_code"]
                try:
                    book = Book.query.filter_by(book_code=book_code).first()
                    if book and book.availability == "1":
                        return jsonify({
                            "message": "This book is avalable to Issue",
                            "book_code": book_code,
                            "book_name": str(book.book_name),
                            "availability": True,
                        }), 200
                    else:
                        return jsonify({
                            "message": "This Book is already issued.",
                            "book_code": book_code,
                            "book_name": str(book.book_name),
                            "availability": False,
                        }), 203
                except Exception as e:
                    return jsonify({
                            "message": "Can't found this book.",
                            "book_code": book_code,
                            "availability": False,
                        }), 303
            else:
                # add the book
                book_name = request.form.get("book_name")
                book_code = request.form.get("book_code")
                student_name = request.form.get("student_name")
                student_class = request.form.get("student_class")
                admition_no = request.form.get("admition_no")
                issue_date = date.today()
                return_date = str(request.form.get("return_date"))
                
                try:
                    borrowBook = BorrowBook(
                        book_name = book_name,
                        book_code = book_code,
                        student_name = student_name,
                        student_class = student_class,
                        admition_no = admition_no,
                        issue_date = issue_date,
                        return_date = datetime.strptime(return_date, "%Y-%m-%d"),
                        datetime = datetime.now()
                    )

                    book = Book.query.filter_by(book_code=book_code, book_name=book_name).first()
                    book.availability = 0

                    db.session.add(borrowBook)
                    db.session.commit()

                    flash("successfully issued the book for "+student_name+".", "success")
                    return redirect("/dashboard/returnbook")
                except Exception as e:
                    flash("this book cant be added now. Internal Server Error.", "danger")

        logdin = True
        return render_template(
            "admin/dashboard/issuebook.html", impData=impdata, logdin=logdin
        )

    return redirect("/signin")

# Main return route
@app.route("/dashboard/returnbook", methods=["GET", "POST"])
def returnbook():
    if "logdin" in session and session["logdin"]:
        logdin = True
        IssuedBooks = BorrowBook.query.filter_by(returned="0").all()
        return render_template(
            "admin/dashboard/returnbook.html", impData=impdata, logdin=logdin, IssuedBooks=IssuedBooks
        )

    return redirect("/signin")


# return book
@app.route("/dashboard/return/<book_code>/<sno>", methods=["GET", "POST"])
def returnTheBook(book_code, sno):
    if "logdin" in session and session["logdin"]:
        logdin = True
        try:
            bookDetail = BorrowBook.query.filter_by(sno=sno, book_code=book_code).first()
            print(book_code + "  -    " + sno)
            bookDetail.returning_date = datetime.today()
            bookDetail.returned = 1
            db.session.commit()
            
            book = Book.query.filter_by(book_code = book_code).first()
            book.availability = 1
            db.session.commit()
            flash("book is returned to the library successfully.", "success")
        except Exception as e:
            print(e)
            flash("cant return book now. Internal Server Error.", "danger")
        
        return redirect('/dashboard')

    return redirect("/signin")

if __name__ == "__main__":
    app.run(debug=True)
