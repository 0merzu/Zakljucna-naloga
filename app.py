from flask import Flask, render_template, request, redirect, flash, session
from tinydb import TinyDB, Query
import folium
from datetime import datetime, time
from dateutil.relativedelta import relativedelta, SU


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
        total_location_votes = len(db.search(User.location.exists()))
        host_count = len(db.search(User.role == 'host'))

        if email == 'admin@admin' and password == 'admin':
            session['admin'] = True
            return redirect('/admin')

        if user and user['password'] == password and user['role'] == 'host' and total_location_votes >= 5:
            return redirect('/host_dashboard')
        
        if user and user['password'] == password and user['role'] == 'host' and total_location_votes <= 5:
            if user.get('location'):
                return redirect('/final_dashboard')
        
        if user and user['password'] == password and user['role'] == 'host' and total_location_votes <= 5:
            return redirect('/vote_dashboard')
        
        if user and user['password'] == password and user['role'] == 'guest':
            return redirect('/final_dashboard')
        
        else:
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/host_dashboard', methods=['GET', 'POST'])
def host_dashboard():
    email = session.get('email')

    host_count = len(db.search(User.role == 'host'))
    vote_count = len(db.search(User.location.exists()))

    locations = [u['location'] for u in db.all() if 'location' in u]

    if locations:
        top_location = max(set(locations), key=locations.count)
        location_final = top_location

        coordinate_mapping = {
            'location-1': [46.1068177, 14.4466918],
            'location-2': [46.0569465, 14.5057515],
            'location-3': [46.0510833, 14.5060582],
            'location-4': [46.065944, 14.520100],
        }

        coords = coordinate_mapping.get(top_location)

        m = folium.Map(location=coords, zoom_start=13, width='600px', height='400px')
        folium.Marker(coords, popup=f"Lokacija: {top_location}").add_to(m)
        loc_map = m._repr_html_()

    session['loc_map'] = loc_map

    if request.method == 'POST':
        IG_handle = request.form['IG_handle']
        znamka = request.form['znamka']
        model = request.form['model']
        letnik = request.form['letnik']
        engine = request.form['engine']
        power = request.form['power']


        if IG_handle[0] != '@':
            IG_handle = "@" + IG_handle
        db.update({'IG_handle': IG_handle}, User.email == email)

        if db.search(User.email == email):
            db.update({
                'znamka': znamka,
                'model': model,
                'letnik': letnik,
                'engine': engine,
                'power': power
            }, User.email == email)

            return redirect('/final_dashboard')

    return render_template(
        'host_dashboard.html',
        host_count=host_count,
        vote_count=vote_count,
        location_final=location_final,
        loc_map=loc_map
    )

@app.route('/final_dashboard', methods=['GET', 'POST'])
def final_dashboard():
    hosts = db.search(User.role == 'host')

    email = session.get('email')
    locations = [u['location'] for u in db.all() if 'location' in u]
    print(locations)

    if locations:
        top_location = max(set(locations), key=locations.count)
        location_final = top_location

        coordinate_mapping = {
            'location-1': [46.1068177, 14.4466918],
            'location-2': [46.0569465, 14.5057515],
            'location-3': [46.0510833, 14.5060582],
            'location-4': [46.065944, 14.520100],
        }

        coords = coordinate_mapping.get(top_location)

        m = folium.Map(location=coords, zoom_start=13, width='600px', height='400px')
        folium.Marker(coords, popup=f"Lokacija: {top_location}").add_to(m)
        loc_map = m._repr_html_()


 

    now = datetime.now()
    next_sunday = now + relativedelta(weekday=SU(+1))
    next_sunday = datetime.combine(next_sunday.date(), time(11))
    next_sunday = next_sunday.strftime("%d.%m.%Y ob %H:%M")

    vote_count = len(db.search(User.location.exists()))




    return render_template('final_dashboard.html', next_sunday=next_sunday,loc_map=loc_map, users=hosts, vote_count=vote_count, location_final=location_final)

@app.route('/vote_dashboard', methods=['GET', 'POST'])
def vote_dashboard():
    email = session.get('email')

    locations = {
        'location-1': [46.1068177, 14.4466918],
        'location-2': [46.0569465, 14.5057515],
        'location-3': [46.0510833, 14.5060582],
        'location-4': [46.065944, 14.520100],
    }

    locs = {}
    for key, coords in locations.items():                                                   #Explanation
        m = folium.Map(location=coords, zoom_start=13, width='100%', height='200px')
        folium.Marker(coords, popup=f"Lokacija: {key}").add_to(m)
        locs[key] = m._repr_html_()

    if request.method == 'POST':
        location = request.form['location']
        
        if db.search(User.email == email):
            db.update({'location': location}, User.email == email)
            return redirect('/host_dashboard')

    return render_template('vote_dashboard.html', locs=locs)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        db.truncate()
        return redirect('/admin')

    hosts = db.search(User.role == 'host')
    guests = db.search(User.role == 'guest')

    location1_count = len(db.search(User.location == 'location-1'))
    location2_count = len(db.search(User.location == 'location-2'))
    location3_count = len(db.search(User.location == 'location-3'))
    location4_count = len(db.search(User.location == 'location-4'))

    return render_template('admin_dashboard.html',
                           host_count=len(hosts),
                           guest_count=len(guests),
                           location1_count=location1_count,
                           location2_count=location2_count,
                           location3_count=location3_count,
                           location4_count=location4_count)


if __name__ == '__main__':
    app.run(debug=True)
