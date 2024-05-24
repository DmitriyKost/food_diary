from os import getenv
import os
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from database import db, User, Meal, MealEntry
from dotenv import load_dotenv
import datetime

# Loading variables from configuration file
load_dotenv(".env")

app = Flask(__name__)
app.secret_key = getenv("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JWT_SECRET_KEY'] = getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'  
app.config['JWT_COOKIE_SECURE'] = False  
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  
db.init_app(app)
jwt = JWTManager(app)


# Main page that contains all the features
# Redirects to login page if token not found
@app.route('/')
@jwt_required(optional=True)
def index():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(login=current_user).first()
        selected_date = request.args.get('date')
        if not user:
            return redirect(url_for('login'))

        
        if selected_date:
            meals = MealEntry.query.filter_by(user_id=user.id, date=selected_date).all()
        else:
            selected_date = datetime.date.today().strftime('%Y-%m-%d')
            meals = MealEntry.query.filter_by(user_id=user.id, date=selected_date).all()

        
        total_calories_today = sum(meal.calories for meal in meals)
        total_protein_today = sum(meal.protein for meal in meals)
        total_carbs_today = sum(meal.carbs for meal in meals)
        total_fat_today = sum(meal.fat for meal in meals)

        
        daily_calories_needed = calculate_daily_calories(user)
        daily_protein_needed, daily_carbs_needed, daily_fat_needed = calculate_daily_nutrient_needs(user)

        
        calories_percentage = (total_calories_today / daily_calories_needed) * 100 if daily_calories_needed > 0 else 0
        protein_percentage = (total_protein_today / daily_protein_needed) * 100 if daily_protein_needed > 0 else 0
        carbs_percentage = (total_carbs_today / daily_carbs_needed) * 100 if daily_carbs_needed > 0 else 0
        fat_percentage = (total_fat_today / daily_fat_needed) * 100 if daily_fat_needed > 0 else 0

        
        return render_template('index.html', 
                               user=current_user, 
                               meals=meals, 
                               total_calories_today=total_calories_today, 
                               daily_calories_needed=daily_calories_needed, 
                               calories_percentage=calories_percentage,
                               total_protein_today=total_protein_today,
                               daily_protein_needed=daily_protein_needed,
                               protein_percentage=protein_percentage,
                               total_carbs_today=total_carbs_today,
                               daily_carbs_needed=daily_carbs_needed,
                               carbs_percentage=carbs_percentage,
                               total_fat_today=total_fat_today,
                               daily_fat_needed=daily_fat_needed,
                               fat_percentage=fat_percentage,
                               selected_date=selected_date)

    return redirect(url_for('login'))


def calculate_daily_calories(user):
    # Mifflin-St Jeor Equation
    if user.sex == 'male':
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
    
    daily_calories_needed = bmr * user.activity_coefficient
    return daily_calories_needed


def calculate_daily_nutrient_needs(user):
    # General recommendations, TODO: customize
    daily_protein_grams = user.weight * 1.6  
    daily_carb_grams = 300  
    daily_fat_grams = 70  
    
    return daily_protein_grams, daily_carb_grams, daily_fat_grams


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        sex = request.form['sex']
        activity_coefficient = request.form['activity_coefficient']
        
        if User.query.filter_by(login=login).first():
            flash('User already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(
            login=login,
            age=int(age),
            weight=float(weight),
            height=float(height),
            sex=sex,
            activity_coefficient=float(activity_coefficient)
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        user = User.query.filter_by(login=login).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.login, expires_delta=datetime.timedelta(hours=1))
            response = make_response(redirect(url_for('index')))
            set_access_cookies(response, access_token)
            return response
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    unset_jwt_cookies(response)
    return response


# Adds a specified meal name to users list.
# Each user can have their own list of meal names.
@app.route('/add_meal', methods=['GET', 'POST'])
@jwt_required()
def add_meal():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first()

        if not user:
            return redirect(url_for('login'))
 
        name = request.form['name']
        new_meal = Meal(
            name=name,
            user_id = user.id
        )
        db.session.add(new_meal)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_meal.html')


# Adding a meal information with specified meal name and data
@app.route('/add_meal_entry', methods=['GET', 'POST'])
@jwt_required()
def add_meal_entry():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first()

        if not user:
            return redirect(url_for('login'))
        
        meal_id = request.form['meal_id']
        date = request.form['date']
        calories = request.form['calories']
        protein = request.form['protein']
        carbs = request.form['carbs']
        fat = request.form['fat']
        
        new_entry = MealEntry(
            user_id=user.id,
            meal_id=meal_id,
            date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat
        )
        
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))

    current_user = get_jwt_identity()
    user = User.query.filter_by(login=current_user).first()

    if not user:
        return redirect(url_for('login'))

    meals = Meal.query.filter_by(user_id=user.id).all()
    return render_template('add_meal_entry.html', meals=meals)


@app.route('/meal_entry/<int:meal_entry_id>', methods=['GET', 'POST'])
@jwt_required()
def meal_entry(meal_entry_id):
    meal_entry = MealEntry.query.get_or_404(meal_entry_id)
    
    if request.method == 'POST':
        meal_entry.calories = request.form['calories']
        meal_entry.protein = request.form['protein']
        meal_entry.carbs = request.form['carbs']
        meal_entry.fat = request.form['fat']
        
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('meal_entry.html', meal_entry=meal_entry)


@app.route('/delete_meal_entry/<int:meal_entry_id>', methods=['POST'])
@jwt_required()
def delete_meal_entry(meal_entry_id):
    meal_entry = MealEntry.query.get_or_404(meal_entry_id)
    
    db.session.delete(meal_entry)
    db.session.commit()
    return make_response(redirect(url_for('index')))


@app.route('/update_profile', methods=['GET', 'POST'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(login=current_user).first()

    if not user:
        return redirect(url_for('logout'))

    if request.method == 'POST':
        user.weight = float(request.form['weight'])
        user.height = float(request.form['height'])
        user.age = int(request.form['age'])
        user.activity_coefficient = float(request.form['activity_coefficient'])
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update_profile.html', user=user)

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
