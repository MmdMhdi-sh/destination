from flask import (
    Flask,  
    redirect,
    render_template,
    request, 
    session
)
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)

app.secret_key = "you are a b****"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)


"""
Models
"""
class User(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username

class City(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return '<City %r>' % self.name
    
with app.app_context():
    db.create_all()

"""
functions
"""
def set_user_session(user, session):
    session['username'] = user.username

def user_exits(user_username):
    user = User.query.filter_by(username=user_username).first()
    if user:
        return True
    return False


def is_authenticated(session):
    session_username = session['username']
    user = User.query.filter_by(username=session_username).first()
    if user:
        return True
    return False



"""
Views
"""
@app.route('/', methods=['POST', 'GET'])
def home_page():
    if request.method == "POST":
        city_name = request.form['name']
        new_city = City(name=city_name)
        print("new city = ", new_city)

        try:
            db.session.add(new_city)
            db.session.commit()
            return redirect('/')
        except:
            return "City cannot be submitted"
    else:
        cities_list = City.query.order_by(City._id).all()
        return render_template('pages/home.html', cities=cities_list)


@app.route('/register', methods=['GET', 'POST'])
def user_register_view():
    if request.method == 'POST':
        print("request.form = ", request.form)
        user_username = request.form['username']
        user_password = request.form['password']
        print("user_username = ", user_username)
        print("user_password = ", user_password)
        new_user = User(username=user_username, password=user_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/register')
        except:
            return "You cannot register!"
    else:
        users_list = User.query.order_by(User._id).all()
        return render_template('pages/register.html', users=users_list)  

@app.route('/login', methods=['POST', 'GET'])
def login_view():
    if request.method == 'POST':
        user_username = request.form['username']
        user_password = request.form['password']
        if user_exits(user_username):
            user_obj = User.query.filter_by(username=user_username).first()
            if user_password == user_obj.password:
                set_user_session(user_obj, session)
                print("session =", session)
                redirect('/')
            else:
                return "wrong password"
        else:
            return "Username does not exist!"
    return render_template("pages/login.html")
    



@app.route('/delete/<int:id>')
def city_delete_view(id):
    city_obj = City.query.get_or_404(id)
    try:
        db.session.delete(city_obj)
        db.session.commit()
        return redirect('/')
    except:
        return "You cannot delete this city!"

@app.route('/detail/<int:id>', methods=['GET'])
def city_detail_view(id):
    city_obj = City.query.get_or_404(id)
    return render_template('pages/city.html', city=city_obj)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def city_update_view(id):
    city_obj = City.query.get_or_404(id)
    if request.method == "POST":
        city_obj.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'City cannot be updated'
    return render_template('pages/city_update.html', city=city_obj)
    

if __name__ == '__main__':
    app.run(debug=True)
