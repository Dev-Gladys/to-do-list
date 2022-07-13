from flask import Flask, render_template, redirect,url_for,request,flash
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo-users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)



login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CREATE TABLE IN DB FOR LOGIN DETAILS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB.
#db.create_all()


##CREATES TABLE IN  DB FOR USER LIST OF TODOS
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    complete = db.Column(db.Boolean)
db.create_all()



@app.route('/')
def home():
    return render_template("index-todo-list.html")





@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            new_user = User(
                email=request.form.get('email'),
                name=request.form.get('name'),
                password=generate_password_hash(password=request.form.get('password'),
                                                     method='pbkdf2:sha256:2000',
                                                     salt_length=20))
            #the yellow indication is due to the Mexins but it works

            db.session.add(new_user)
            db.session.commit()

             # Log in and authenticate user after adding details to database.
            login_user(new_user)

    return render_template("register-todo.html",logged_in=current_user.is_authenticated)



@app.route('/login',methods=["GET", "POST"])
def login():
    if request.method=="POST":
        user = User.query.filter_by(email=request.form.get('email')).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        elif not check_password_hash(user.password, request.form.get('password')):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
            # Email exists and password correct
        else:
            login_user(user)
            return redirect(url_for("add"))

    return render_template("login-todo.html", logged_in=current_user.is_authenticated)


@app.route("/start")
def start():
    todo_list = Todo.query.all()
    return render_template("todo-list.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("start"))


@app.route("/update/<int:id>")
def update(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("start"))


@app.route("/delete/<int:id>")
def delete(id):
    task = Todo.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("start"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)












