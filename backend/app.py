from datetime import timedelta, datetime
from flask import (
    Flask,  
    redirect,
    render_template,
    request, 
    session,
    url_for
)
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


app = Flask(__name__)

app.secret_key = "thisisasecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

"""
functions
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""
Models
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username

class City(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    posts = db.relationship('Post', backref='city', lazy=True)
    def __repr__(self):
        return '<City %r>' % self.name
    
class Post(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.String(150), db.ForeignKey('city._id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Post %r>' % self._id

class Comment(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.String(150), db.ForeignKey('post._id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime,
        nullable=False, unique=False, index=False,
        default=datetime.utcnow)

with app.app_context():
    db.create_all()

"""
Forms
"""
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')
    


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
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    users_list = User.query.order_by(User.id).all()
    return render_template('pages/register.html', form=form, users=users_list)  

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home_page'))
    return render_template('pages/login.html', form=form) 
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/posts/<city_name>', methods=['GET', 'POST'])
def city_posts_view(city_name):
    if request.method == 'POST':
        # post_user = User.query.filter_by(username=request.form['username'])
        post_city = City.query.filter_by(name=city_name).first()
        post_city_id = post_city._id
        post_content = request.form['content']
        new_post = Post(city_id=post_city_id, content=post_content)
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('city_posts_view', city_name=post_city.name))
        except:
            return 'You cannot add this post!'
    print("city_name = ",city_name)
    city_obj= City.query.filter_by(name=city_name).first()
    posts_list = City.query.filter_by(name=city_name).first().posts
    return render_template('city/city_posts.html', city=city_obj, posts=posts_list)

@app.route('/posts/<int:id>', methods=['POST', 'GET'])
def post_detail_view(id):
    post_obj = Post.query.get_or_404(id)
    if request.method == 'POST':
        comment_user = current_user
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        comment_post = Post.query.get_or_404(id)
        comment_content = request.form['content']
        new_comment = Comment(user_id=comment_user.id, post_id=comment_post._id, content=comment_content)
        try:
            db.session.add(new_comment)
            db.session.commit()
            comments_list = Comment.query.filter_by(post_id=id).all()
            return redirect(url_for('post_detail_view', id=comment_post._id))
        except:
            return 'You cannot add this comment!'
    comments_list = Comment.query.filter_by(post_id=id).all()
    return render_template('post/detail.html', post=post_obj, comments=comments_list)



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
    return render_template('city/city_detail.html', city=city_obj)

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


"""
API Views
"""
@app.route('/api/post/<int:id>/comments')
def city_comments_api_view(id):
    comments = Comment.query.filter_by(post_id=id).all()
    username = User.query.get_or_404(1).username
    serializer = [{"username": username, "content": comment.content} for comment in comments]
    return render_template('api/comment.html', comments=serializer)

if __name__ == '__main__':
    app.run(debug=True)
