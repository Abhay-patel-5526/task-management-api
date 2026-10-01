from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, make_response, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash , check_password_hash
import jwt
from datetime import datetime,timedelta, timezone
from flask_cors import CORS

app=Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200))
    password=db.Column(db.String(200))
    role=db.Column(db.String(200))

    task=db.relationship("Tasks", back_populates="user", cascade="all,delete-orphan")
class Tasks(db.Model):
    __tablename__="tasks"
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"))
    title=db.Column(db.String(200))
    description=db.Column(db.String(200))
    status=db.Column(db.String(200))
    priority=db.Column(db.String(200))
    created_at=db.Column(db.String(200))

    user=db.relationship("Users", back_populates="task")
    
with app.app_context():
    db.create_all()


app.secret_key="qwertyhjmnbvcdswertyulmnbvcdrtyukmnbvfrtyuilmnhgf"
JWT_SECRET="dcvbhjhgvbniuygbnmloiuhgbniuytrdgy6ruytfvbnmjuy6trfvbjiu7tfghj"



#test
# @app.route("/")
# def t():
#     return "hii"

@app.route("/data", methods=["GET","POST"])
def data():
    u=Users.query.all()
    r=Tasks.query.all()
    # return "df"
    return render_template("data.html",u=u,r=r)

#user routes
@app.route("/api/registration", methods=["POST"])
def registration():
    data=request.json
    name=data.get("name")
    password_raw=data.get("password")
    
    role=data.get("role")
    
    if name is None or name=="":
        return jsonify({"error":"name not recieved"}),400
    
    if role is None or role=="":
        return jsonify({"error":"role not recieved"}),400
    if password_raw is None or password_raw=="":
        return jsonify({"error":"password not recieved"}),400
    
    password=generate_password_hash(password_raw)


    
    


    user=Users(name=name,password=password,role=role)
    
    db.session.add(user)

    db.session.commit()

    token=jwt.encode({
                "user_id":user.id,
                "exp":datetime.now(timezone.utc) + timedelta(hours=5)
            },
            JWT_SECRET,algorithm="HS256"
        )

    return jsonify({"token":token}),201

@app.route("/api/login",methods=["POST"])
def login():
    data=request.json
    id=data.get("id")
    password=data.get("password")
    query=db.session.get(Users,id)

    if query is None:
        return jsonify({"error":"user don't exist"}),401
    

    if id != None and id !="" and password != None and password != "" :
        if check_password_hash(query.password,password):
            token=jwt.encode({
            "user_id":query.id,
            "exp":datetime.now(timezone.utc) + timedelta(hours=5)},
            JWT_SECRET,algorithm="HS256")

            return jsonify({"token":token}),200
        else:
            return jsonify({"error":"invalid password"}),400


    return jsonify({"error":"enough detail isn't recieved!"}),400

@app.route("/api/tasks",methods=["POST"])
def create():
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]

    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
    
    user_id=data["user_id"]
    print(user_id)
    requestjson=request.json
    title=requestjson.get("title")
    description=requestjson.get("description")
    status =requestjson.get("status")
    priority=requestjson.get("priority")
    if None in [title,description,status,priority]:
        return jsonify({"error":"not all parameter recieved!"}),400
    tasks=Tasks(title=title,description=description,status=status,priority=priority,user_id=user_id,created_at=datetime.now(timezone.utc))

    db.session.add(tasks)
    db.session.commit()
    return jsonify({"status":"task added"}),201

@app.route("/api/tasks")
def view():
    #queryparameters
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]
    
    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
        
    user_id=data["user_id"]
    priority=request.args.get("priority")
    if priority is not None:
        query=Tasks.query.filter(Tasks.user_id==user_id,Tasks.priority==priority).all()
    else:
        query=Tasks.query.filter(Tasks.user_id==user_id).all()
    Task=[]
    for a in query:
        Task.append({"id":a.id,"title":a.title,"description":a.description,"priority":a.priority,"status":a.status})

    return jsonify(Task)

@app.route("/api/tasks/<int:id>")
def view_byid(id):
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]
        
    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
            
    user_id=data["user_id"]
    u=db.session.get(Users,user_id)
    a=db.session.get(Tasks,id)
    if a is None:
        return jsonify({"error":"id don't exist"}),404
    if a.user_id==user_id or u.role=="admin":
        return jsonify({"id":a.id,"title":a.title,"description":a.description,"priority":a.priority,"status":a.status})
    else:
        return jsonify({"error":"You are not allowed to access that task"}),403
    return "h"



@app.route("/api/tasks/<int:id>",methods=["PATCH"])
def update(id):
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]
        
    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
            
    user_id=data["user_id"]

    task_data=db.session.get(Tasks,id)
    if task_data is None:
        return jsonify({"error":"no data exist"}),404


    query= db.session.get(Users,user_id)
    if query.role=="admin" or task_data.user_id==user_id:
        taskup=request.json
        title=taskup.get("title")
        description=taskup.get("description")
        status=taskup.get("status")
        priority=taskup.get("priority")

        if title!=None and title!="":
            task_data.title=title

        if description!=None and description!="":
            task_data.description=description

        if status!=None and status!="":
            task_data.status=status

        if priority!=None and priority!="":
            task_data.priority=priority
        db.session.commit()
        return jsonify({"id":id,"user_id":task_data.user_id,"title":task_data.title,"description":task_data.description,"status":task_data.status,"priority":task_data.priority})

    else:
        return jsonify({"error":"user is not allowed"}),403



@app.route("/api/tasks/<int:id>",methods=["DELETE"])
def delete(id):
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]
        
    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
            
    user_id=data["user_id"]
    task_data=db.session.get(Tasks,id)
    if task_data is None:
        return jsonify({"error":"no data exist"}),404

    query= db.session.get(Users,user_id)
    if query.role=="admin" or task_data.user_id==user_id:
        db.session.delete(task_data)
        db.session.commit()

        return jsonify({"status":"deleted task"})
    else:
        return jsonify({"error":"user not allowed"}),403



#Admin special
@app.route("/users",methods=["GET"])
def adminuser():
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]

    
        
    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
            
    user_id=data["user_id"]
    user=db.session.get(Users,user_id)
    if user.role=="admin":
        users=Users.query.all()
        user_data=[]
        for a in users:
            user_data.append({"id":a.id,"name":a.name,"role":a.role})
        return jsonify(user_data)
        #add loop to store user and then display them! id name role

    else:
        return jsonify({"error":"User not allowed"}),403



@app.route("/viewtask")
def admintaskview():
    auth=request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error":"auth request!"}),401
    token=auth.split(" ")[1]

    p=request.args.get("priority")
    pa=request.args.get("page")
    l=request.args.get("limit")

    
        
    try:
        data=jwt.decode(token, JWT_SECRET,algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error":"Invalid or expiered token"}),401
            
    user_id=data["user_id"]
    user=db.session.get(Users,user_id)
    if user.role=="admin":
        if p!=None and pa==None and l==None:
            tasks=Tasks.query.filter(Tasks.priority==p).all()
        elif p==None and pa!=None and l!=None:
            pa=int(pa)
            l=int(l)
            tasks=Tasks.query.offset((pa-1)*l).limit(l).all()
        elif p!=None and pa!=None and l!=None:
            pa=int(pa)
            l=int(l)
            tasks=Tasks.query.filter(Tasks.priority==p).offset((pa-1)*l).limit(l).all()
        else:
            tasks=Tasks.query.all()
        
        tasks_data=[]
        for a in tasks:
            tasks_data.append({
                "id":a.id,
                "title":a.title,
                "description":a.description,
                "user_id":a.user_id,
                "status":a.status,
                "priority":a.priority,
                "created_at":a.created_at

            })
        return jsonify(tasks_data)
        #add loop to store user and then display them! id name role

    else:
        return jsonify({"error":"User not allowed"}),403



if __name__=="__main__":
    app.run(debug=True)