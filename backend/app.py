from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
db = SQLAlchemy(app)

class City(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    # def __repr__(self):
    #     return '<User %r>' % self.name
with app.app_context():
    db.create_all()

    
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
