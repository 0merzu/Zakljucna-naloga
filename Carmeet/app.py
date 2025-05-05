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

@app.route('/host_dashboard', methods=['GET', 'POST'])
def host_dashboard():
    email = session.get('email')
    

    if request.method == 'POST':
        IG_handle = request.form['IG_handle']
        znamka = request.form['znamka']
        model = request.form['model']
        letnik = request.form['letnik']
        engine = request.form['engine']
        power = request.form['power']

        if IG_handle[0] == "@":
            db.update({'IG_handle': IG_handle}, User.email == email)
        else:
            IG_handle = "@" + IG_handle
            db.update({'IG_handle': IG_handle}, User.email == email)
        
        if db.search(User.email == email):
            db.update({'znamka': znamka, 'model': model, 'letnik': letnik, 'engine': engine, 'power': power}, User.email == email)


    host_count = len(db.search(User.role == 'host'))
    vote_count = len(db.search(User.location.exists()))                    

    locations = [u['location'] for u in db.all() if 'location' in u]

    if locations:
        top_location = max(set(locations), key=locations.count)
        location_final = top_location
    else:
        location_final = "Glasovanje še ni zaključeno"  

    locations = {
        'location-1': [46.1068177, 14.4466918],
        'location-2': [46.0569465, 14.5057515],
        'location-3': [46.0510833, 14.5060582],
        'location-4': [46.065944, 14.520100],
    }

    for key, coords in locations.items():
        if key == top_location:                                         
            m = folium.Map(location=coords, zoom_start=13, width='600px', height='400px')
            folium.Marker(coords, popup=f"Lokacija: {top_location}").add_to(m)
            loc_map = m._repr_html_()

    session['loc_map'] = loc_map

    return render_template(
        'host_dashboard.html',
        host_count=host_count,
        vote_count=vote_count,
        location_final=location_final,
        loc_map = loc_map
    )



if __name__ == '__main__':
    app.run(debug=True)
