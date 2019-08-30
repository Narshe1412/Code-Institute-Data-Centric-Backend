import unittest
import json
from bson.objectid import ObjectId
from app import app


class TestAPI(unittest.TestCase):
    """
    Test cases for API endpoints
    """

    def setUp(self):
        """
        Setup unit tests
        """
        self.app = app
        self.client = self.app.test_client()
        self.mockTask = {
            'title': 'test title',
            'reference': 'test ref',
            'description': 'test desc',
            'timeWorked': [],
            'status': 'test status',
            'visible': True
        }
        self.mockEditedTask = {
            'title': 'edited title',
            'reference': 'edited ref',
            'description': 'edited desc',
            'timeWorked': [],
            'status': 'edited status',
            'visible': True
        }

    def test_Tasks_GET_all_tasks(self):
        """
        should return an array of active tasks
        should return status 200
        """
        response = self.client.get(path="/tasks")
        self.assertIs(type(json.loads(response.get_data())), list)
        self.assertEqual(response.status_code, 200)

    def test_Tasks_POST_create_new_task(self):
        """
        should return the task just created
        should return status 200
        """
        response = self.client.post(
            path="/tasks", json=self.mockTask, content_type="application/json")
        response_data = json.loads(response.get_data(as_text=True))
        response_data.pop("_id")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, self.mockTask)

    def test_Tasks_POST_create_new_task_bad_data(self):
        """
        should return status 400
        """
        response = self.client.post(
            path="/tasks", json={"nothing": "here"}, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_Task_PUT_edit_an_existing_task(self):
        """
        should return status 200
        should return an updated entry
        """
        # Create initial post and obtain its id
        response = self.client.post(path='/tasks', json=self.mockTask,
                                    content_type='application/json')
        response_data = json.loads(response.get_data(as_text=True))
        task_id = response_data['_id']['$oid']

        # Execute request
        path = '/tasks/' + task_id
        response = self.client.put(
            path, json=self.mockEditedTask, content_type='json')
        self.assertEqual(response.status_code, 200)

    def test_Task_PUT_edit_an_existing_task(self):
        """
        should return status 400
        """
        # Create initial post and obtain its id
        response = self.client.post(path='/tasks', json=self.mockTask,
                                    content_type='application/json')
        response_data = json.loads(response.get_data(as_text=True))
        task_id = response_data['_id']['$oid']

        # Execute request
        path = '/tasks/' + task_id
        response = self.client.put(
            path, json={"nothing": "there"}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_DELETE_an_existing_task(self):
        """
        should return status 200
        should return a dictionary with the number of elements deleted = 1
        """
        # Create initial post and obtain its id
        response = self.client.post(path='/tasks', json=self.mockTask,
                                    content_type='application/json')
        response_data = json.loads(response.get_data(as_text=True))
        task_id = response_data['_id']['$oid']

        # Execute request
        url = '/tasks/' + task_id
        response = self.client.delete(url)
        response_data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {"deleted_count": 1})

    def test_DELETE_a_non_existing_task(self):
        """
        should return status 200
        should return a dictionary with the number of elements deleted = 0
        """
        task_id = "123456789012345678901234"
        # Execute request
        url = '/tasks/' + task_id
        response = self.client.delete(url)
        response_data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {"deleted_count": 0})


if __name__ == '__main__':
    unittest.main()
