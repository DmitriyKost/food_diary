# Food diary
## Description
The service is a food diary and meal tracking application that allows users to monitor their daily food intake and track their nutritional intake. Users can create an account, log in, and record their meals along with their nutritional information. They can also view their daily caloric intake, protein, carbohydrates, and fat consumption.
### Features
- User Authentication: Users can create an account and log in securely using their credentials.
- Meal Tracking: Users can add, view, edit, and delete meals along with their nutritional information such as calories, protein, carbohydrates, and fat.
- Nutritional Analysis: The service calculates and displays the total daily intake of calories, protein, carbohydrates, and fat, allowing users to monitor their nutritional goals.
- Profile Management: Users can update their profile information including age, weight, height, sex, and activity coefficient to calculate their daily caloric needs.


## How does it works?
### Technologies Used:
- Python for backend
- SQLite as database
- Flask-SQLAlchemy is used as an ORM tool
- JWT is used for user authentication and authorization
- HTML/CSS for the frontend 
- Jinja2 templating engine is used to generate dynamic HTML content

Other requirements specified in [requirements file](./requirements.txt).
## How to run it
You might want to edit the [config file](./.env).

To run it locally execute following commands:
```sh
python3 -m venv vevn
source venv/bin/activate
pip install -r requirements.txt
python3 init_db.py
```
If you want to just test/debug run this:
```sh
python3 app.py
```
Else (you can set your own `-w` - number of workers and port number):
```sh 
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```
To run it with Docker:
```sh 
docker build -t food_diary .
docker run -d -p 8080:8080 food_diary
```
