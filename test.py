import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/posters'   # posters will be saved here

# Make sure the folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ======================
# Local storage (instead of DynamoDB)
# ======================
users = {}        # {email: {"name": name, "password": hashed_password}}
admins = {}       # {email: {"name": name, "password": hashed_password, "role": "admin"}}
feedbacks = []    # list of feedback dicts

# =====================
# Movie Data (static)
# =====================
movies = {
    "MOV001": {
        "title": "MARCO",
        "description": "It is a ruthless gangster seeking vengeance for his brother's brutal murder.",
        "poster": "Images/Action.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    },
    "MOV002": {
        "title": "JUMANJI",
        "description": "It is a fan-film prequel that reveals the origin of the cursed game.",
        "poster": "Images/Advanture.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV003": {
        "title": "GOLMAAL: FUN UNLIMITED",
        "description": "It is about four mischievous, con-artist-Gopal,Madhav,Lucky & Laxman who are expelled from college.",
        "poster": "Images/Comady.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    },
    "MOV004": {
        "title": "THE DRAMA",
        "description": "This movie exploring intense human experiences,relationships and personal struggle.",
        "poster": "Images/Drama.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV005": {
        "title": "MALEFICENT",
        "description": "This is a live-action Disney film that reimagines Sleeping Beauty from the villain's perspective, exploring her backstory as a betrayed fairy protector.",
        "poster": "Images/Fantasy.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    },
    "MOV006": {
        "title": "THE CONJURING: LAST RITES",
        "description": "It is the final entry in the main conjuring series, following Ed and Lorraine Warren as they face a definitive, high-stakes case based on the haunting of the Smurl family Pennsylvania.",
        "poster": "Images/HORRER.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["11:00 AM", "4:00 PM", "8:00 PM"]
    },
    "MOV007": {
        "title": "THE SEARCH",
        "description": "The Search movie follows a man looking for life outside the universe who instead finds connection with a grieving family.",
        "poster": "Images/Mistory.jpg",
        "theaters": ["PVR Cinemas", "INOX", "Cinepolis"],
        "showtimes": ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]
    }
    # ... keep the rest of your movies here ...
}

# ====================
# Routes
# ====================

@app.route('/')
def index():
    return render_template('index.html', movies=movies)

@app.route('/home')
def home():
    return render_template('index.html', movies=movies)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/adminDashbord')
def adminDashbord():
    return render_template('AdminDashbord.html')

@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminL&S.html')

@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    if movie_id in movies:
        movie_data = movies[movie_id]
        return render_template('movie.html', movie_data=movie_data)
    else:
        return "Movie not found", 404
# =========================
# User Signup
# =========================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('L&S.html')

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if email in users:
        return render_template('L&S.html', msg="User already exists")

    hashed_password = generate_password_hash(password)
    users[email] = {"name": name, "password": hashed_password}

    msg = "Registration Complete. Please Login to your account"
    return render_template('L&S.html', msg=msg)

# =========================
# User Login
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('L&S.html')

    email = request.form['email']
    password = request.form['password']

    if email not in users:
        return render_template('L&S.html', msg="User not found")

    stored_password = users[email]["password"]

    if check_password_hash(stored_password, password):
        return render_template('index.html', name=users[email]["name"])
    else:
        return render_template('L&S.html', msg="Wrong password")

# =========================
# Admin Signup
# =========================
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'GET':
        return render_template('AdminL&S.html')

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if email in admins:
        return render_template('AdminL&S.html', msg="Admin already exists")

    hashed_password = generate_password_hash(password)
    admins[email] = {"name": name, "password": hashed_password, "role": "admin"}

    msg = "Admin registration successful. Please login."
    return render_template('AdminL&S.html', msg=msg)

# =========================
# Admin Login
# =========================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('AdminL&S.html')

    email = request.form['email']
    password = request.form['password']

    if email not in admins:
        return render_template('AdminL&S.html', msg="Admin not found")

    stored_password = admins[email]["password"]

    if check_password_hash(stored_password, password):
        return render_template('AdminDashbord.html', name=admins[email]["name"], movies=movies)
    else:
        return render_template('AdminL&S.html', msg="Wrong password")

# =========================
# Contact Form
# =========================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')

    username = request.form['username']
    email = request.form['email']
    feedback = request.form['feedback']

    feedbacks.append({"username": username, "email": email, "feedback": feedback})

    msg = "Your feedback has been submitted successfully!"
    return render_template('contact.html', msg=msg)

#===========================
# admin dashbord
#===========================

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        movie_id = request.form['movie_id']
        title = request.form['title']
        description = request.form['description']
        theaters = request.form['theaters'].split(',')
        showtimes = request.form['showtimes'].split(',')

        # Handle poster file upload
        poster_file = request.files['poster']
        filename = secure_filename(poster_file.filename)
        poster_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        poster_file.save(poster_path)

        # Save movie info (new posters go into posters folder)
        movies[movie_id] = {
            "title": title,
            "description": description,
            "poster": f"posters/{filename}",
            "theaters": theaters,
            "showtimes": showtimes
        }

        msg = f"Movie '{title}' added successfully!"
        return render_template('AdminDashbord.html', msg=msg, movies=movies)

    return render_template('AdminDashbord.html', movies=movies)


@app.route('/delete/<movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if movie_id in movies:
        # Optionally also remove the poster file if it was uploaded
        poster_path = os.path.join('static', movies[movie_id]['poster'])
        if os.path.exists(poster_path) and poster_path.startswith("static/posters/"):
            os.remove(poster_path)

        # Remove movie from dictionary
        del movies[movie_id]

    return render_template('AdminDashbord.html', msg=f"Movie {movie_id} deleted!", movies=movies)


if __name__ == '__main__':
    app.run(debug=True)