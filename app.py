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
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

# Routes
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/tasks', methods=['GET'])
def get_tasks():
    result = mongo.db.tasks.find()
    return json_util.dumps(result)


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_by_id(task_id):
    result = mongo.db.tasks.find({"_id": ObjectId(task_id)})
    return json_util.dumps(result)


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task_by_id(task_id):
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
    result = mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    return {"deleted_count": result.deleted_count}


@app.route('/tasks', methods=['POST'])
def insert_task():
    try:
        task = get_task_from_request_form(request)
        result = mongo.db.tasks.insert_one(task)
        return json_util.dumps(get_task_by_id(result.inserted_id))
    except Exception as err:
        abort(400)


# Helper functions
def get_task_by_id(task_id):
    return mongo.db.tasks.find_one({"_id": ObjectId(task_id)})


# @app.route('/add_task')
# def add_task():
#     return render_template("addTask.html", categories=mongo.db.categories.find())


# @app.route('/insert_task', methods=['POST'])
# def insert_task():
#     tasks = mongo.db.tasks
#     tasks.insert_one(request.form.to_dict())
#     return redirect(url_for('get_tasks'))


# @app.route('/edit_task/<task_id>')
# def edit_task(task_id):
#     found_task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
#     all_categories = mongo.db.categories.find()
#     return render_template("editTask.html", task=found_task, categories=all_categories)


# @app.route('/update_task/<task_id>', methods=['POST'])
# def update_task(task_id):
#     tasks = mongo.db.tasks
#     tasks.update(
#         {
#             "_id": ObjectId(task_id)
#         },
#         {
#             "task_name": request.form.get('task_name'),
#             "category_name": request.form.get('category_name'),
#             "task_description": request.form.get('task_description'),
#             "due_date": request.form.get('due_date'),
#             "is_urgent": request.form.get('is_urgent')
#         })
#     return redirect(url_for('get_tasks'))


# @app.route('/delete_task/<task_id>')
# def delete_task(task_id):
#     mongo.db.tasks.remove({"_id": ObjectId(task_id)})
#     return redirect(url_for('get_tasks'))


# @app.route('/get_categories')
# def get_categories():
#     return render_template('categories.html', categories=mongo.db.categories.find())


# @app.route('/edit_category/<category_id>')
# def edit_category(category_id):
#     return render_template('editCategory.html',
#                            category=mongo.db.categories.find_one({'_id': ObjectId(category_id)}))


# @app.route('/update_category/<category_id>', methods=['POST'])
# def update_category(category_id):
#     mongo.db.categories.update(
#         {'_id': ObjectId(category_id)},
#         {'category_name': request.form.get('category_name')})
#     return redirect(url_for('get_categories'))


# @app.route('/delete_category/<category_id>')
# def delete_category(category_id):
#     mongo.db.categories.remove({'_id': ObjectId(category_id)})
#     return redirect(url_for('get_categories'))


# @app.route('/insert_category', methods=['POST'])
# def insert_category():
#     category_doc = {'category_name': request.form.get('category_name')}
#     mongo.db.categories.insert_one(category_doc)
#     return redirect(url_for('get_categories'))


# @app.route('/add_category')
# def add_category():
#     return render_template('addCategory.html')

def get_task_from_request_form(request):
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
