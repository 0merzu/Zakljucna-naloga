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
            return redirect('/login')

        db.insert({'name': name, 'surname': surname , 'email': email, 'password': password, 'role': role})
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        
        session['email'] = email
        password = request.form['password']

        user = db.get(User.email == email)

        host_count = len(db.search(User.role == 'host'))

        if user and user['password'] == password and user['role'] == 'host' and host_count >= 5:
            flash(f'Prijava uspešna! Pozdravljen, {user["name"]}.', 'success')
            return redirect('/host_dashboard')
        
        if user and user['password'] == password and user['role'] == 'host' and host_count <= 5:
            flash(f'Prijava uspešna! Pozdravljen, {user["name"]}.', 'success')
            return redirect('/vote_dashboard')
        
        if user and user['password'] == password and user['role'] == 'guest':
            flash(f'Prijava uspešna! Pozdravljen, {user["name"]}.', 'success')
            return redirect('/guest_dashboard')
        
        
        else:
            return redirect('/login')

    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)
