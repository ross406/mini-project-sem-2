from flask import Flask , request , jsonify
from flask_cors import CORS 
from flask_pymongo import PyMongo 
from bson import ObjectId
import hashlib
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import json
import logging
from validation import validatePostInput
app = Flask(__name__)
# connect your mongodb after installation
app.config["MONGO_URI"]='mongodb://localhost:27017/demo2'
mongo = PyMongo(app)

CORS(app)
db = mongo.db.demo2
users_collection = db["users"]
posts_collection = db["posts"]

jwt = JWTManager(app) # initialize JWTManager
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) # define the life span of the token

# Register a new user
@app.route("/api/users/register", methods=["POST"])
def register():
	new_user = request.get_json() # store the json body request
	new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
	doc = users_collection.find_one({"email": new_user["email"]}) # check if user exist
	if not doc:
		users_collection.insert_one(new_user)
		return jsonify({'msg': 'User created successfully'}), 201
	else:
		return jsonify({'msg': 'Email already exists'}), 409

# Login with that user to get Access Token
@app.route("/api/users/login", methods=["post"])
def login():
	login_details = request.get_json() # store the json body request
	user_from_db = users_collection.find_one({'email': login_details['email']})  # search for user in database

	if user_from_db:
		encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
		if encrpted_password == user_from_db['password']:
			access_token = create_access_token(identity=(str(user_from_db['_id']),user_from_db['email'])) # create jwt token
			return jsonify(access_token=access_token), 200

	return jsonify({'msg': 'The email or password is incorrect'}), 401

# Get All Posts Or Add New Post
@app.route('/api/posts',methods=["GET","POST"])
@jwt_required()
def getpost():
    if request.method == "GET":
        userid = get_jwt_identity()[0]
        print(userid)
        posts =[]
        for i in db.find():
            posts.append({"_ID":str(ObjectId(i["_id"])),"name":i["name"],"text":i["text"],"user":i["user"],"likes":[],"comments":[]})
        return jsonify(posts)
    elif request.method == "POST":
        errors = validatePostInput(request.json)
        # print(errors)
        userid = get_jwt_identity()[0]
        # print(email[0])
        id = db.insert_one({"name":request.json["name"],"text":request.json["text"],"user":userid,"likes":[],"comments":[]}).inserted_id
        logging.debug('This is a debug message',id)
        return jsonify(str(ObjectId(id)))
        # return id

# delete / update / get single post
@app.route('/api/posts/<id>',methods=["DELETE","PUT","GET"])
@jwt_required()
def deleteputget(id):
    if request.method == "DELETE":
        db.delete_one({"_id":ObjectId(id)})
        return jsonify({"message":"deleted"})
    elif request.method == "PUT":
        db.update_one({"_id":ObjectId(id)},{"$set":{
            "name":request.json["name"],
            "text":request.json["text"],
            "user":request.json["user"]
        }})
        return jsonify({"message":"updated"})
    elif request.method == "GET":
        res = db.find_one({"_id":ObjectId(id)})
        return {"_ID":str(ObjectId(res["_id"])),"name":res["name"],"text":res["text"],"user":res["user"],"likes":res["likes"],"comments":res["comments"]}

# Like a Post
@app.route('/api/posts/like/<id>',methods=["POST"])
@jwt_required()
def likepost(id):
    userid = get_jwt_identity()[0]
    print(userid)
    user = users_collection.find_one({"_id": ObjectId(userid)}) 
    print(user)
    if(user):
        post = db.find_one({"_id":ObjectId(id)})
        print(post)
        if not post["likes"]:
            db.update_one({"_id":ObjectId(id)},{"$set":{
                "likes":[userid],
            }})
            res = db.find_one({"_id":ObjectId(id)})
            return {"_ID":str(ObjectId(res["_id"])),"name":res["name"],"text":res["text"],"user":res["user"],"likes":res["likes"],"comments":res["comments"]}
        elif userid in post["likes"]:
            return jsonify({'msg': 'User already liked this Post'}), 400
        else:
            likes = post["likes"]
            likes.unshift(userid)
            db.update_one({"_id":ObjectId(id)},{"$set":{
                "likes":likes,
            }})
            res = db.find_one({"_id":ObjectId(id)})
            return {"_ID":str(ObjectId(res["_id"])),"name":res["name"],"text":res["text"],"user":res["user"],"likes":res["likes"],"comments":res["comments"]}
    return jsonify({'msg': 'User dose not exist'}), 400   


# UnLike a Post
@app.route('/api/posts/unlike/<id>',methods=["POST"])
@jwt_required()
def unlikepost(id):
    userid = get_jwt_identity()[0]
    print(userid)
    user = users_collection.find_one({"_id": ObjectId(userid)}) 
    print(user)
    if(user):
        post = db.find_one({"_id":ObjectId(id)})
        print(post)
        if not post["likes"]:
           return jsonify({'msg': 'There are no likes on this post'}), 400
        elif userid in post["likes"]:
            likes = post["likes"]
            likes.remove(userid)
            db.update_one({"_id":ObjectId(id)},{"$set":{
                "likes":likes,
            }})
            res = db.find_one({"_id":ObjectId(id)})
            return {"_ID":str(ObjectId(res["_id"])),"name":res["name"],"text":res["text"],"user":res["user"],"likes":res["likes"],"comments":res["comments"]}
        else:
            return jsonify({'msg': 'You have not yet liked the post'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400  



   

@app.route('/getone/<id>',methods=["GET"])
def getone(id):
    res = db.find_one({"_id":ObjectId(id)})
    print(res)
    return {"_ID":str(ObjectId(res["_id"])),"name":res["name"],"email":res["email"],"password":res["password"]}

# if __name__ == "__main__":
#     app.run(port=5000, dubug=True)
