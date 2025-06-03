from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__, template_folder='template')


UPLOAD_FOLDER = r"C:\Users\reani\OneDrive\Documents\Summer Bootcamp 2025\WEEK 1\image"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="",  
    database="db_login"
)

@app.route('/')
def home():
    return render_template("login.html") 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM tbl_register WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return redirect('/profile')
        else:
            return "Invalid credentials. Please try again.", 401

    return render_template("login.html")
    


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        
        image = request.files['image']
        image_path = None
        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)  

        
        cursor = db.cursor()
        query = "INSERT INTO tbl_register (image, name, birthday, address, username, password) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (image.filename, name, birthday, address, username, password)
        cursor.execute(query, values)
        db.commit()
        cursor.close()

        return redirect('/')
    return render_template("register.html")

@app.route('/profile')
def profile():
    cursor = db.cursor(dictionary=True)
    query = "SELECT name, birthday, address, image FROM tbl_register ORDER BY id_user DESC LIMIT 1"
    cursor.execute(query)
    user = cursor.fetchone()
    cursor.close()

    if user and user['birthday']:
        try:
            
            birth_date = datetime.strptime(user['birthday'], '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            user['age'] = age
        except ValueError:
            user['age'] = "Invalid birthday format"

    if user and user['image']:
        user['image_path'] = url_for('static', filename='uploads/' + user['image'])

    return render_template("profile.html", user=user)


if __name__ == '__main__':
    app.run(debug=True)