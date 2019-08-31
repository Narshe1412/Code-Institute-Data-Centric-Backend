import os
from flask import Flask, render_template, redirect, request, url_for, abort, make_response, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson import json_util
import json

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "data_driven"
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)


@app.after_request
def after_request(response):
    """
    Add CORS headers to each request
    """
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

# Routes
@app.route('/')
def home():
    """
    Displays API definitions
    """
    return render_template("index.html")


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Obtains the full list of tasks on the system
    """
    result = mongo.db.tasks.find()
    return json_util.dumps(result)


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_by_id(task_id):
    """
    Obtains a single task by its id
    """
    result = mongo.db.tasks.find({"_id": ObjectId(task_id)})
    return json_util.dumps(result)


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task_by_id(task_id):
    """
    Updates a single task by ID

    Returns
    -------
    Status code 400
        if a required field is not provided, it will return 400 bad request code
    """
    try:
        updated_task = get_task_from_request_form(request)
        tasks = mongo.db.task

        tasks.update(
            {
                "_id": ObjectId(task_id)
            },
            {
                "title": updated_task['title'],
                "reference": updated_task['reference'],
                "description": updated_task['description'],
                "status": updated_task['status'],
                "visible": updated_task['visible']
            })

        return json_util.dumps(get_task_by_id(task_id))
    except:
        abort(400)


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task_by_id(task_id):
    """
    Deletes a task from the system based on its id
    """
    result = mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    return {"deleted_count": result.deleted_count}


@app.route('/tasks', methods=['POST'])
def insert_task():
    """
    Inserts a single task into the system

    Returns
    -------
    Status code 400
        if a required field is not provided, it will return 400 bad request code
    """
    try:
        task = get_task_from_request_form(request)
        result = mongo.db.tasks.insert_one(task)
        return json_util.dumps(get_task_by_id(result.inserted_id))
    except Exception as err:
        abort(400)


# Timer endpoints

@app.route('/times/<task_id>', methods=['GET'])
def get_times_by_task_id(task_id):
    """
    Obtains all the times by the id of its task
    """
    try:
        result = mongo.db.tasks.aggregate([
            {"$match": {"_id": ObjectId(task_id)}},
            {"$replaceRoot": {"newRoot": {"timeWorkd": "$timeWorked"}}}
        ])
        return json_util.dumps(result)
    except Exception as err:
        print("error", err)
        abort(400)


@app.route('/times/<task_id>', methods=['POST'])
def add_time_by_task_id(task_id):
    """
    Adds a new time object to the specified task id
    """
    try:
        json_data = request.get_json()
        time_from_request = {
            "timestamp": json_data["timestamp"],
            "duration": json_data["duration"]}
        result = mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {
            '$push': {'timeWorked': time_from_request}})
        return json_util.dumps({"added": result.modified_count})
    except Exception as err:
        abort(400)


@app.route('/times/<task_id>', methods=['DELETE'])
def delete_time_entry_by_task_id(task_id):
    """
    Delete a timer item that matches the id and the timestamp 
    """
    try:
        json_data = request.get_json()
        timestamp = json_data["timestamp"]
        result = mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {
            '$pull': {'timeWorked': {"timestamp": timestamp}}})
        return json_util.dumps({"removed": result.modified_count})
    except Exception as err:
        abort(400)

# Helper functions


def get_task_by_id(task_id):
    return mongo.db.tasks.find_one({"_id": ObjectId(task_id)})


def get_task_from_request_form(request):
    """
    Parses a request from the API endpoint attempting to extract the JSON information and transform
    it on a python dict

    Returns
    -------
    dict
        a dictionary obtained from the provided json

    Raises
    ------
    ValueError
        If a required field is missing
    """
    json_data = request.get_json()
    # Required fields
    if "title" not in json_data:
        raise ValueError("Required field is missing")
    if "reference" not in json_data:
        raise ValueError("Required field is missing")
    if "status" not in json_data:
        raise ValueError("Required field is missing")

    task_from_request = {
        'title': json_data['title'],
        'reference': json_data['reference'],
        'description': json_data['description'],
        'timeWorked': [],
        'status': json_data['status'],
        'visible': "visible" in json_data
    }

    return task_from_request


# Main
if __name__ == "__main__":
    if(os.environ.get("WINDIR")):
        app.run(host="localhost", port=8080, debug=True)
    else:
        app.run(host=os.environ.get("IP"), port=int(
            os.environ.get("PORT")), debug=True)
