from flask import Flask, render_template, request, redirect, flash, session
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = 'carmeet_secret'

db = TinyDB('db.json')
User = Query()

@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if db.search(User.email == email):
            flash('Email already registered.', 'error')
            return redirect('/login')

        db.insert({'name': name, 'surname': surname , 'email': email, 'password': password, 'role': role})
        flash('Successfully registered!', 'success')
        return redirect('/login')

    return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True)
