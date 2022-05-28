import sqlite3
import smtplib, ssl

from flask import Flask,render_template,request,session,redirect
from random import randint

def otp():
    return randint(100000,999999)

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'data_management'

c = sqlite3.connect('database.db',check_same_thread=False)
db = c.cursor()


message = ''
yuvit = ''
messg = ''
mail = ''
response = ''
password_data = ''
user = ''
finish = ''
incorrect = 0
show = 0
already = 0
count = 0
log_out = 0
change = 0
books = 0
mss = 0
log = 0
bro = False
var = otp()
value = ''

db.execute('''CREATE TABLE IF NOT EXISTS users(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              email TEXT NOT NULL,
              phone_number INTEGER NOT NULL,
              address TEXT NOT NULL)''')

db.execute('''CREATE TABLE IF NOT EXISTS books_data(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL,
               title TEXT NOT NULL,
               author TEXT NOT NULL,
               ISBN TEXT NOT NULL,
               genre TEXT NOT NULL)''')

c.commit()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET',"POST"])
def login():
    global user
    if request.method == 'GET':
        if 'username' not in session:
            return render_template('login.html')
        return render_template('index.html',already = 1)

    name = request.form.get('username')
    password = request.form.get('password')
    print(name, password, 'hello')
    check = db.execute('SELECT password FROM users WHERE username = (?) ',(name,)).fetchone()
    checker = db.execute("SELECT username FROM users WHERE username = (?)", (name,)).fetchone()
    print(checker,check)
    if checker == None:
        return render_template('login.html',response = 'Username or password incorrect')
    if password not in check:
        return render_template('login.html',response = 'Username or password incorrect')
    session['username'] = name
    user = name
    return render_template('index.html',show = 1)

@app.route('/register',methods = ['GET',"POST"])
def register():
    if request.method == 'GET':
        if 'username' not in session:
            return render_template('Register.html')
        return render_template('index.html',already = 1)

    name = request.form.get('username')
    password = request.form.get('password')
    confirmation = request.form.get('confirmation')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')
    check = db.execute('SELECT username FROM users WHERE username = (?) ',(name,)).fetchone()
    print(check)
    if confirmation == password:
        if check == None:
            db.execute("INSERT INTO users(username, password, email, phone_number, address) VALUES (?, ?, ?, ?, ?)", (name, password, email, phone_number, address))
            c.commit()
            return render_template('login.html',response = 'Registration complete please sign in to continue')
    return render_template('register.html', message = 'Username already taken or passwords do not match')

@app.route('/torent',methods = ['GET','POST'])
def to_rent():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('rent.html')
        render_template('rent.html')
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        genre = request.form.get('genre')
        user = session['username']
        print(user)
        db.execute('INSERT INTO books_data(username,title,author,ISBN,genre) VALUES(?,?,?,?,?)', (user,title,author,isbn,genre))
        c.commit()
        return render_template('index.html', mss = 1)         

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        session.clear()
        return render_template('index.html',log_out = 1)
    return render_template('index.html')

@app.route('/forgot', methods = ['GET','POST'])
def forgot():
    global var,user, count, mail
    if request.method == 'GET':
        return render_template('forgot.html')
    user = request.form.get('username')
    email = db.execute('SELECT email FROM users WHERE username = (?) ',(request.form.get('username'),)).fetchone()
    email = list(email)
    for i in email:
        if count == 0:
            mail = i
        count += 1
    s = smtplib.SMTP('smtp.gmail.com', 587)
  
    # start TLS for security
    s.starttls()
  
    # Authentication
    s.login("batrayuvit@gmail.com", "vqazpjgojpagdyej")
  
    # message to be sent
    message = f"Dear {user} your OTP is {var}"
  
    # sending the mail
    s.sendmail("batrayuvit@gmail.com", mail, message)
  
    # terminating the session
    s.quit()
    return render_template('verify.html')

@app.route('/browse',methods = ['POST','GET'])
def browse():
    if request.method == 'GET':
        value = db.execute("SELECT title,author,ISBN,genre FROM books_data").fetchall()
        l = []
        for i in value:
            j = i[2]
            p = f'https://covers.openlibrary.org/b/ISBN/{j}-M.jpg'
            l.append(p)
        return render_template('browse.html', value = value, l = l)
    if request.method == "POST":
        a = request.form['title']
        value = db.execute("SELECT title,author,ISBN,genre FROM books_data WHERE title LIKE ? ",('%'+a+'%',)).fetchall()
        if value == []:
            return render_template('message.html', messg = 'Sorry the requisite book is not available')
        l = []
        for i in value:
            j = i[2]
            p = f'https://covers.openlibrary.org/b/ISBN/{j}-M.jpg'
            l.append(p)
        return render_template('browse.html', value = value, l = l)

@app.route('/verify', methods = ["POST","GET"])
def verify():
    if request.method == 'GET':
        return render_template('verify.html')
    global var
    OTP = request.form.get('OTP')
    print(var)
    print(OTP)
    if str(var) == str(OTP):
        print("hello")
        return render_template('new_password.html')
    return render_template('index.html', incorrect = 1)

@app.route('/new', methods = ['POST','GET'])
def new():
    global user
    if request.method == "GET":
        return render_template('new_password.html')
    password = request.form.get('password')
    confirmation = request.form.get('confirmation')
    if password != confirmation:
        return render_template('new_password.html',password_data = 'passwords don\'t match')
    db.execute('UPDATE users SET password = (?) WHERE username = (?)',(password,user))
    c.commit()
    return render_template('index.html', change = 1)

@app.route('/get_book/<title>', methods = ['GET', 'POST'])
def get_book(title):
    if 'username' in session:
        global user
        data = db.execute('SELECT username FROM books_data WHERE title = ?',(title,)).fetchall()
        number = []
        l = set()
        for i in data:
            l.add(i[0])
        for j in l:
            address = db.execute('SELECT phone_number,address FROM users WHERE username = ?',(j,)).fetchall()
            print(address)
            for n in address:
                number.append(n)
        if request.method == "GET":
            return render_template('get_book.html',number = number, user = user)
    return redirect('/login')

@app.route('/remove', methods = ["GET","POST"])
def remove():
    global finish,bro
    if 'username' in session:
        global user
        if request.method == "GET":
            data = db.execute('SELECT * FROM books_data WHERE username = ?', (user,)).fetchall()
            return render_template('remove.html', data = data)
        title = request.form.get('title')
        dat = db.execute('SELECT title FROM books_data WHERE username = ?', (user,)).fetchall()
        for i in dat:
            if title in i:
                bro = True
        if bro:
            db.execute('DELETE FROM books_data WHERE username = ? AND title = ?', (user,title))
            c.commit()
            return redirect('remove')
        return render_template('remove.html', yuvit = 'Please enter exact name')

    return render_template('login.html')

if __name__ == '__main__':

    app.run()