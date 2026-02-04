from flask import Flask, request, render_template
import os
from werkzeug.utils import secure_filename
# remove comment when get dynamodb working
import key_config as keys
import boto3
from botocore.exceptions import ClientError
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/posters'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# remove 8 comment when get dynamodb working

#======================
# DynamoDB connection
#======================

dynamodb = boto3.resource('dynamodb',
    region_name='us-east-1',
    aws_access_key_id=keys.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=keys.AWS_SECRET_ACCESS_KEY,
    aws_session_token=keys.AWS_SESSION_TOKEN,
)
users_table = dynamodb.Table('users')
admin_table = dynamodb.Table('admins')
contact_table = dynamodb.Table('ContactForm')

#=====================
# SNS
#=====================

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:604665149129:aws_capstone_topic'

sns = boto3.client(
    'sns',
    region_name='us-east-1',
    aws_access_key_id=keys.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=keys.AWS_SECRET_ACCESS_KEY,
    aws_session_token=keys.AWS_SESSION_TOKEN,
)

def send_notification(subject, message):
    """Helper function to publish a message to SNS topic"""
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Notification sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending notification: {e}")

#==================
# MOVIE DATA 
#==================
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
}


#====================
# Home route
#====================

@app.route('/')
def index():
    return render_template('index.html', movies=movies)

@app.route('/home')
def home():
    return render_template('index.html', movies=movies)

# for direction to about page
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


#============================
# User Signup
#============================


# SIGNUP API
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('L&S.html')  # Optional signup page

    # POST method
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    users_table.put_item(
        Item={
            'email': email,
            'name': name,
            'password': hashed_password
        }
    )

    # Send SNS notification
    send_notification("New User Signup", f"User {name} ({email}) has registered.")

    msg = "Registration Complete. Please Login to your account"
    return render_template('L&S.html', msg=msg)


#============================
# User Login 
#============================


# LOGIN API
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('L&S.html')

    # POST login
    email = request.form['email']
    password = request.form['password']

    response = users_table.get_item(Key={'email': email})

    if 'Item' not in response:
        return render_template('L&S.html', msg="User not found")

    stored_password = response['Item']['password']

    if check_password_hash(stored_password, password):
        return render_template('index.html', name=response['Item']['name'])
    else:
        return render_template('L&S.html', msg="Wrong password")

#=========================
# Admin signup 
#=========================

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'GET':
        return render_template('AdminL&S.html')

    # POST
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    admin_table.put_item(
        Item={
            'email': email,
            'name': name,
            'password': hashed_password,
            'role': 'admin'
        }
    )

     # Send SNS notification
    send_notification("New Admin Signup", f"Admin {name} ({email}) has registered.")

    msg = "Admin registration successful. Please login."
    return render_template('AdminL&S.html', msg=msg)

#=========================
# Admin Login 
#=========================


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('AdminL&S.html')

    # POST
    email = request.form['email']
    password = request.form['password']

    response = admin_table.get_item(Key={'email': email})

    if 'Item' not in response:
        return render_template('AdminL&S.html', msg="Admin not found")

    stored_password = response['Item']['password']

    if check_password_hash(stored_password, password):
        return render_template('AdmiDashbord.html', name=response['Item']['name'])
    else:
        return render_template('AdminL&S.html', msg="Wrong password")


#===================
# Contact Form
#===================

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')

    # POST method
    username = request.form['username']
    email = request.form['email']
    feedback = request.form['feedback']

    contact_table.put_item(
        Item={
            'email': email,       # Partition key
            'username': username,
            'feedback': feedback
        }
    )

    # Send SNS notification
    send_notification("New Contact Form Submission", f"{username} ({email}) submitted feedback: {feedback}")

    msg = "Your feedback has been submitted successfully!"
    return render_template('contact.html', msg=msg)

#==================
# Admin Dashbord
#==================

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        movie_id = request.form['movie_id']
        title = request.form['title']
        description = request.form['description']
        theaters = request.form['theaters'].split(',')
        showtimes = request.form['showtimes'].split(',')

        poster_file = request.files['poster']
        filename = secure_filename(poster_file.filename)
        poster_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        poster_file.save(poster_path)

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
        poster_path = os.path.join('static', movies[movie_id]['poster'])
        if os.path.exists(poster_path) and movies[movie_id]['poster'].startswith("posters/"):
            os.remove(poster_path)
        del movies[movie_id]
    return redirect(url_for('admin_dashboard'))





if __name__ == '__main__':
    app.run(debug=True)
