from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
import hashlib
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import json
import logging
import time
from validation import validatePostInput

app = Flask(__name__)
# connect your mongodb after installation
app.config["MONGO_URI"] = 'mongodb://localhost:27017/demo'
mongo = PyMongo(app)

CORS(app)
db = mongo.db.demo2
users_collection = db["users"]
posts_collection = db["posts"]
profile_collection = db["profile"]

jwt = JWTManager(app)  # initialize JWTManager
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)  # define the life span of the token


# Register a new user
@app.route("/api/users/register", methods=["POST"])
def register():
    new_user = request.get_json()  # store the json body request
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()  # encrpt password
    doc = users_collection.find_one({"email": new_user["email"]})  # check if user exist
    if not doc:
        users_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Email already exists'}), 409


# Login with that user to get Access Token
@app.route("/api/users/login", methods=["post"])
def login():
    login_details = request.get_json()  # store the json body request
    user_from_db = users_collection.find_one({'email': login_details['email']})  # search for user in database

    if user_from_db:
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            access_token = create_access_token(
                identity=(str(user_from_db['_id']), user_from_db['email'], user_from_db['name']))  # create jwt token
            return jsonify(access_token=access_token), 200

    return jsonify({'msg': 'The email or password is incorrect'}), 401


# Get All Posts Or Add New Post
@app.route('/api/posts', methods=["GET", "POST"])
@jwt_required()
def getpost():
    if request.method == "GET":
        userid = get_jwt_identity()[0]
        print(userid)
        posts = []
        for i in posts_collection.find():
            posts.append(
                {"_ID": str(ObjectId(i["_id"])), "name": i["name"], "text": i["text"], "user": i["user"],
                 "likes": i["likes"],
                 "comments": i["comments"]})
        return jsonify(posts)
    elif request.method == "POST":
        # errors = validatePostInput(request.json)
        # print(errors)
        userid = get_jwt_identity()[0]
        # print(email[0])
        id = posts_collection.insert_one(
            {"name": request.json["name"], "text": request.json["text"], "user": userid, "likes": [],
             "comments": []}).inserted_id
        res = posts_collection.find_one({"_id": ObjectId(id)})
        return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                "likes": res["likes"], "comments": res["comments"]}
        


# delete / update / get single post
@app.route('/api/posts/<id>', methods=["DELETE", "PUT", "GET"])
@jwt_required()
def deleteputget(id):
    if request.method == "DELETE":
        posts_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "deleted"})
    elif request.method == "PUT":
        posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
            "name": request.json["name"],
            "text": request.json["text"],
            "user": request.json["user"]
        }})
        return jsonify({"message": "updated"})
    elif request.method == "GET":
        res = posts_collection.find_one({"_id": ObjectId(id)})
        return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                "likes": res["likes"], "comments": res["comments"]}


# Like a Post
@app.route('/api/posts/like/<id>', methods=["POST"])
@jwt_required()
def likepost(id):
    userid = get_jwt_identity()[0]
    print(userid)
    user = users_collection.find_one({"_id": ObjectId(userid)})
    print(user)
    if (user):
        post = posts_collection.find_one({"_id": ObjectId(id)})
        if post: 
            print(post)
            if not post["likes"]:
                posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
                    "likes": [userid],
                }})
                res = posts_collection.find_one({"_id": ObjectId(id)})
                return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                        "likes": res["likes"], "comments": res["comments"]}
            elif userid in post["likes"]:
                return jsonify({'msg': 'User already liked this Post'}), 400
            else:
                likes = post["likes"]
                likes.append(userid)
                posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
                    "likes": likes,
                }})
                res = posts_collection.find_one({"_id": ObjectId(id)})
                return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                        "likes": res["likes"], "comments": res["comments"]}
        return jsonify({'msg': 'Post dose not exist'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400


# UnLike a Post
@app.route('/api/posts/unlike/<id>', methods=["POST"])
@jwt_required()
def unlikepost(id):
    userid = get_jwt_identity()[0]
    print(userid)
    user = users_collection.find_one({"_id": ObjectId(userid)})
    print(user)
    if (user):
        post = posts_collection.find_one({"_id": ObjectId(id)})
        print(post)
        if not post["likes"]:
            return jsonify({'msg': 'There are no likes on this post'}), 400
        elif userid in post["likes"]:
            likes = post["likes"]
            likes.remove(userid)
            posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
                "likes": likes,
            }})
            res = posts_collection.find_one({"_id": ObjectId(id)})
            return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                    "likes": res["likes"], "comments": res["comments"]}
        else:
            return jsonify({'msg': 'You have not yet liked the post'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400


# Comment a Post
@app.route('/api/posts/comment/<id>', methods=["POST"])
@jwt_required()
def commentpost(id):
    userid = get_jwt_identity()[0]
    print(userid)
    user = users_collection.find_one({"_id": ObjectId(userid)})
    print(user)
    if (user):
        post = posts_collection.find_one({"_id": ObjectId(id)})
        print(post)
        if not post["comments"]:
            comment = {"id": time.time(), "name": request.json["name"], "text": request.json["text"], "user": userid}
            posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
                "comments": [comment]
            }})
            res = posts_collection.find_one({"_id": ObjectId(id)})
            return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                    "likes": res["likes"], "comments": res["comments"]}
        else:
            comments = post["comments"]
            comment = {"id": time.time(), "name": request.json["name"], "text": request.json["text"], "user": userid}
            comments.append(comment)
            posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
                "comments": comments,
            }})
            res = posts_collection.find_one({"_id": ObjectId(id)})
            return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                    "likes": res["likes"], "comments": res["comments"]}
    return jsonify({'msg': 'User dose not exist'}), 400


# Delete a Comment
@app.route('/api/posts/comment/<id>/<comment_idx>', methods=["DELETE"])
@jwt_required()
def deletecomment(id, comment_idx):
    userid = get_jwt_identity()[0]
    print(userid)
    user = users_collection.find_one({"_id": ObjectId(userid)})
    print(user)
    if (user):
        post = posts_collection.find_one({"_id": ObjectId(id)})
        if (post):
            print(comment_idx)
            comments = post["comments"]
            del comments[int(comment_idx)]
            posts_collection.update_one({"_id": ObjectId(id)}, {"$set": {
                "comments": comments,
            }})
            res = posts_collection.find_one({"_id": ObjectId(id)})
            return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "text": res["text"], "user": res["user"],
                    "likes": res["likes"], "comments": res["comments"]}
        else:
            return jsonify({'msg': 'Post dose not exist'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400


# Get Profile Or Add New Profile or Delete profile and user
@app.route('/api/profile', methods=["GET", "POST", "DELETE"])
@jwt_required()
def get_post_profile():
    if request.method == "GET":
        userid = get_jwt_identity()[0]
        res = profile_collection.find_one({"user": ObjectId(userid)})
        if not res:
            return jsonify({'msg': 'There is no Profile for this User'}), 404
        else:
            return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"],
                    "handle": res["handle"],
                    "company": res["company"], "website": res["website"], "location": res["location"],
                    "bio": res["bio"], "experience": res["experience"], "education": res["education"],
                    "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                    "social": res["social"]}
    elif request.method == "DELETE":
        userid = get_jwt_identity()[0]
        user = users_collection.find_one({"_id": ObjectId(userid)})
        if user:
            profile = profile_collection.find_one({"user": ObjectId(userid)})
            if profile:
                profile_collection.find_one_and_delete({"user": ObjectId(userid)})
            else:
                return jsonify({'msg': 'Profile dose not exist'}), 400

            users_collection.find_one_and_delete({"_id": ObjectId(userid)})
            return jsonify({'msg': 'Profile and user deleted!!!'})
        else:
            return jsonify({'msg': 'User dose not exist'}), 400
    elif request.method == "POST":
        # errors = validatePostInput(request.json)
        # print(errors)
        userid = get_jwt_identity()[0]
        email = get_jwt_identity()[1]
        name = get_jwt_identity()[2]
        profile_fields = {}
        profile_fields['user'] = ObjectId(userid)
        profile_fields['email'] = email
        profile_fields['name'] = name
        profile_fields['experience'] = []
        profile_fields['education'] = []
        profile_fields['date'] = time.time()
        if request.json["handle"]:
            profile_fields['handle'] = request.json["handle"]
        if request.json["company"]:
            profile_fields['company'] = request.json["company"]
        if request.json["website"]:
            profile_fields['website'] = request.json["website"]
        if request.json["location"]:
            profile_fields['location'] = request.json["location"]
        if request.json["bio"]:
            profile_fields['bio'] = request.json["bio"]
        if request.json["status"]:
            profile_fields['status'] = request.json["status"]
        if request.json["githubusername"]:
            profile_fields['githubusername'] = request.json["githubusername"]
        if request.json["skills"]:
            profile_fields['skills'] = request.json["skills"].split(',')

        profile_fields['social'] = {}
        if request.json["youtube"]:
            profile_fields['social']['youtube'] = request.json["youtube"]
        if request.json["twitter"]:
            profile_fields['social']['twitter'] = request.json["twitter"]
        if request.json["facebook"]:
            profile_fields['social']['facebook'] = request.json["facebook"]
        if request.json["linkedin"]:
            profile_fields['social']['linkedin'] = request.json["linkedin"]
        if request.json["instagram"]:
            profile_fields['social']['instagram'] = request.json["instagram"]

        user = users_collection.find_one({"_id": ObjectId(userid)})
        if (user):
            profile = profile_collection.find_one({"user": ObjectId(userid)})
            if profile:
                profile_collection.update_one({"user": ObjectId(userid)}, {"$set": profile_fields})
                res = profile_collection.find_one({"user": ObjectId(userid)})
                return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"],
                        "handle": res["handle"],
                        "company": res["company"], "website": res["website"], "location": res["location"],
                        "bio": res["bio"],
                        "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                        "social": res["social"], "experience": res["experience"], "education": res["education"],
                        "date": res["date"]}
            else:
                profile_handle = profile_collection.find_one({"handle": profile_fields['handle']})
                if profile_handle:
                    return jsonify({'msg': 'That Handle Already Exists'}), 400
                else:
                    profile_id = profile_collection.insert_one(profile_fields).inserted_id
                    return jsonify(str(ObjectId(profile_id)))

        # print(email[0])
        id = profile_collection.insert_one(
            {"name": request.json["name"], "text": request.json["text"], "user": userid, "likes": [],
             "comments": []}).inserted_id
        logging.debug('This is a debug message', id)
        return jsonify(str(ObjectId(id)))
        # return id


# Get All Profiles
@app.route('/api/profile/all', methods=["GET"])
# @jwt_required()
def get_all_profiles():
    profiles = []
    for res in profile_collection.find():
        profiles.append(
            {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"], "handle": res["handle"],
             "company": res["company"], "website": res["website"], "location": res["location"], "bio": res["bio"],
             "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
             "social": res["social"], "experience": res["experience"], "education": res["education"],
             "date": res["date"]}
        )
    return jsonify(profiles)


# Get Profile by handle
@app.route('/api/profile/handle/<handle>', methods=["GET"])
# @jwt_required()
def get_profile_by_handle(handle):
    res = profile_collection.find_one({"handle": handle})
    if not res:
        return jsonify({'msg': 'There is no Profile for this User'}), 404
    else:
        return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"], "handle": res["handle"],
                "company": res["company"], "website": res["website"], "location": res["location"], "bio": res["bio"],
                "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                "social": res["social"], "experience": res["experience"], "education": res["education"],
                "date": res["date"]}


# Get Profile by userId
@app.route('/api/profile/user/<userid>', methods=["GET"])
# @jwt_required()
def get_profile_by_userid(userid):
    res = profile_collection.find_one({"user": ObjectId(userid)})
    if not res:
        return jsonify({'msg': 'There is no Profile for this User'}), 404
    else:
        return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"], "handle": res["handle"],
                "company": res["company"], "website": res["website"], "location": res["location"], "bio": res["bio"],
                "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                "social": res["social"], "experience": res["experience"], "education": res["education"],
                "date": res["date"]}


# add experience to profile
@app.route('/api/profile/experience', methods=["POST"])
@jwt_required()
def add_exp_to_profile():
    # errors = validatePostInput(request.json)
    # print(errors)
    userid = get_jwt_identity()[0]
    new_exp = {}
    new_exp['title'] = request.json["title"]
    new_exp['company'] = request.json["company"]
    new_exp['location'] = request.json["location"]
    new_exp['from'] = request.json["from"]
    new_exp['to'] = request.json["to"]
    new_exp['current'] = request.json["current"]
    new_exp['description'] = request.json["description"]

    user = users_collection.find_one({"_id": ObjectId(userid)})
    if (user):
        profile = profile_collection.find_one({"user": ObjectId(userid)})
        if profile:
            experience = profile["experience"]
            experience.append(new_exp)
            profile_collection.update_one({"user": ObjectId(userid)}, {"$set": {
                "experience": experience
            }})
            res = profile_collection.find_one({"user": ObjectId(userid)})
            return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"],
                    "handle": res["handle"],
                    "company": res["company"], "website": res["website"], "location": res["location"],
                    "bio": res["bio"],
                    "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                    "social": res["social"], "experience": res["experience"], "education": res["education"],
                    "date": res["date"]}
        else:
            return jsonify({'msg': 'Profile dose not exist'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400

# add education to profile
@app.route('/api/profile/education', methods=["POST"])
@jwt_required()
def add_education_to_profile():
    # errors = validatePostInput(request.json)
    # print(errors)
    userid = get_jwt_identity()[0]
    new_education = {}
    new_education['school'] = request.json["school"]
    new_education['degree'] = request.json["degree"]
    new_education['fieldofstudy'] = request.json["fieldofstudy"]
    new_education['from'] = request.json["from"]
    new_education['to'] = request.json["to"]
    new_education['current'] = request.json["current"]
    new_education['description'] = request.json["description"]

    user = users_collection.find_one({"_id": ObjectId(userid)})
    if (user):
        profile = profile_collection.find_one({"user": ObjectId(userid)})
        if profile:
            education = profile["education"]
            education.append(new_education)
            profile_collection.update_one({"user": ObjectId(userid)}, {"$set": {
                "education": education
            }})
            res = profile_collection.find_one({"user": ObjectId(userid)})
            return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"],
                    "handle": res["handle"],
                    "company": res["company"], "website": res["website"], "location": res["location"],
                    "bio": res["bio"],
                    "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                    "social": res["social"], "experience": res["experience"], "education": res["education"],
                    "date": res["date"]}
        else:
            return jsonify({'msg': 'Profile dose not exist'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400

# Delete experience from Profile
@app.route('/api/profile/experience/<exp_idx>', methods=["DELETE"])
@jwt_required()
def delete_experience(exp_idx):
    userid = get_jwt_identity()[0]
    user = users_collection.find_one({"_id": ObjectId(userid)})
    if (user):
        profile = profile_collection.find_one({"user": ObjectId(userid)})
        if (profile):
            experience = profile["experience"]
            del experience[int(exp_idx)]
            profile_collection.update_one({"user": ObjectId(userid)}, {"$set": {
                "experience": experience,
            }})
            res = profile_collection.find_one({"user": ObjectId(userid)})
            return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"],
                    "handle": res["handle"],
                    "company": res["company"], "website": res["website"], "location": res["location"],
                    "bio": res["bio"],
                    "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                    "social": res["social"], "experience": res["experience"], "education": res["education"],
                    "date": res["date"]}
        else:
            return jsonify({'msg': 'profile dose not exist'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400

# Delete education from Profile
@app.route('/api/profile/education/<edu_idx>', methods=["DELETE"])
@jwt_required()
def delete_education(edu_idx):
    userid = get_jwt_identity()[0]
    user = users_collection.find_one({"_id": ObjectId(userid)})
    if (user):
        profile = profile_collection.find_one({"user": ObjectId(userid)})
        if (profile):
            education = profile["education"]
            del education[int(edu_idx)]
            profile_collection.update_one({"user": ObjectId(userid)}, {"$set": {
                "education": education,
            }})
            res = profile_collection.find_one({"user": ObjectId(userid)})
            return {"user": str(ObjectId(res["user"])), "email": res["email"], "name": res["name"],
                    "handle": res["handle"],
                    "company": res["company"], "website": res["website"], "location": res["location"],
                    "bio": res["bio"],
                    "status": res["status"], "githubusername": res["githubusername"], "skills": res["skills"],
                    "social": res["social"], "experience": res["experience"], "education": res["education"],
                    "date": res["date"]}
        else:
            return jsonify({'msg': 'profile dose not exist'}), 400
    return jsonify({'msg': 'User dose not exist'}), 400



@app.route('/getone/<id>', methods=["GET"])
def getone(id):
    res = db.find_one({"_id": ObjectId(id)})
    print(res)
    return {"_ID": str(ObjectId(res["_id"])), "name": res["name"], "email": res["email"], "password": res["password"]}

# if __name__ == "__main__":
#     app.run(port=5000, dubug=True)
