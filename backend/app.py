from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
db = SQLAlchemy(app)

class City(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name
with app.app_context():
    db.create_all()

    
@app.route('/', methods=['POST', 'GET'])
def home_page():
    if request.method == "POST":
        city_name = request.form['name']
        new_city = City(name=city_name)

        try:
            db.session.add(new_city)
            db.session.commit()
            return redirect('/')
        except:
            return "City cannot be submitted"
    else:
        cities_list = City.query.order_by(City._id).all()
        return render_template('pages/home.html', cities=cities_list)

if __name__ == '__main__':
    app.run(debug=True)
