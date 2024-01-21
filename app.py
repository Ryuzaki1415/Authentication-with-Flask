
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask import flash
db = SQLAlchemy()
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db.init_app(app)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



with app.app_context():
    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(20), nullable=False, unique=True)
        password = db.Column(db.String(80), nullable=False)
    
    
    class RegisterForm(FlaskForm):
        username = StringField(validators=[
                            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
        #username is a stringfield with mandatory input, 4<length<20 and render placeholder as username 

        password = PasswordField(validators=[
                                InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

        submit = SubmitField('Register')
    
    
    def validate_username(self, username):  # to check if it is a unique user name
        existing_user_username = User.query.filter_by(  #queriying the database
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

    @app.route("/")
    def home():
        return render_template('home.html')
    
    
    
    
    @app.route("/login",methods=['GET','POST'])
    def login():
        form=LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first() #checking if user exists
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):#check if hash is same and login the user
                    login_user(user)
                    return redirect(url_for('dashboard')) #after sucessful login, take user to dashboard
        return render_template("login.html",form=form)  #passing form to html
    
    
    
    @app.route("/register",methods=['GET','POST'])
    def register():
        form=RegisterForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data) #hash password using bcrypt
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user) #add to the table
            db.session.commit()
            return redirect(url_for('login'))
        return render_template("register.html",form=form)
    
    
    
    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))







    if __name__ == "__main__":
        app.run(debug=True)