
from application import app, db, api
from flask import render_template , request, json, jsonify , Response, redirect, flash, url_for, session
from application.models import User, Course, Enrollment
from application.form import LoginForm, RegisterForm
from flask_restx import Resource

courseData =[
  { "courseID": "1111", "title": "PHP 111", "description": "Intro to PHP", "credits": "3", "term": "Fall, Spring" },
  { "courseID": "2222", "title": "Java 1", "description": "Intro to Java Programming", "credits": "3", "term": "Spring" },
  { "courseID": "3333", "title": "Adv PHP 201", "description": "Advanced PHP Programming", "credits": "3", "term": "Fall" },
  { "courseID": "4444", "title": "Angular 1", "description": "Intro to Angular", "credits": "3", "term": "Fall, Spring" },
  { "courseID": "5555", "title": "Java 2", "description": "Advanced Java Programming", "credits": "4", "term": "Fall" }
];
    


##########################################################################################################

@api.route('/api','/api/')
class GetandPost(Resource):
    
    #Get All
    def get(self):
        return jsonify(User.objects.all())
    
    #POST
    def post(self):
        data = request.get_json()  # ✅ Replace api.payload with this

        # Safety check
        if not data or 'user_id' not in data:
            return {"error": "Missing required field: user_id"}, 400
        

        user = User(user_id=data['user_id'], email=data['email'], first_name=data['first_name'], last_name=data['last_name'])
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id=data['user_id']))
    
@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
    
    #Get One 
    def get(self,idx):
        return jsonify(User.objects(user_id=idx))
    
    # PUT
    def put(self, idx):
        data=api.payload
        User.objects(user_id=idx).update(**data)
        return jsonify(User.objects(user_id=idx))
    
    # DELETE
    def delete(self, idx):
        User.objects(user_id=idx).delete()
        return jsonify("User is deleted!")
    

##########################################################################################################


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", index=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if session.get('username'):
        return redirect(url_for('index'))
    
    form= LoginForm()
    if form.validate_on_submit():
        email= form.email.data
        password= form.password.data
        
        user = User.objects(email=email).first()
        if user and user.check_password(password):        
            flash(f"{user.first_name}, you have successfully logged in!", "success")
            session['user_id'] = user.user_id
            session['username']= user.first_name 
            return redirect('/index')
        else:
            flash("Invalid email or password. Please try again.", "danger")
            
    return render_template("login.html", title="Login", form=form, login=True)

@app.route('/logout')
def logout():
    session['user_id']=False
    session.pop('username', None)
    flash("You have successfully logged out!", "success")
    return redirect(url_for('index'))

@app.route('/courses/')
@app.route('/courses/<term>')
def courses(term=None):
    if term is None:
        term = "Spring 2024"
        classes=Course.objects.all()
    return render_template("courses.html", courseData=classes, courses=True, term=term)


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if session.get('username'):
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user_id= User.objects.count() 
        user_id += 1
        email= form.email.data
        password= form.password.data
        first_name= form.first_name.data
        last_name= form.last_name.data
        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash(f"{user.first_name}, you have successfully registered!", "success")
        return redirect('index')
    return render_template("register.html", title="Register", form=form, register=True)



@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():
    
    if not session.get('username'):
        return redirect(url_for('login'))
    
    
    courseID= request.form.get('courseID')
    courseTitle= request.form.get('title')
    user_id = session.get('user_id')
    
    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID).first():
            flash(f"Oops! You are already registered in this course {courseTitle}!", "danger")
            return redirect(url_for('courses'))
        
        else:
            Enrollment(user_id=user_id, courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")
        
    classes = list(User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
]))
      

    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)


# @app.route("/api/")
# @app.route("/api/<idx>")
# def api(idx=None):
#     if (idx == None):
#         jdata = courseData
#     else:
#         jdata= courseData[int(idx)]
        
#     return Response(json.dumps(jdata), mimetype='application/json')


@app.route("/user")
def user():
    # User(user_id=1, first_name="Harry", last_name="Potter", email="harrypotter@gmail.com", password="123456").save()
    # User(user_id=2, first_name="Tony", last_name="Stark", email="tonystark@gmail.com", password="abc123").save()
    users = User.objects.all()    
    return render_template("user.html", users=users)
     

