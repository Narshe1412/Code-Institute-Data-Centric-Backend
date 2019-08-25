import unittest
import json
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
            path="/tasks", data=self.mockTask, content_type="application/x-www-form-urlencoded")
        response_data = json.loads(response.get_data())
        response_data.pop("_id")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, self.mockTask)

    def test_Tasks_POST_create_new_task_bad_data(self):
        """
        should return status 400
        """
        response = self.client.post(
            path="/tasks", data={"nothing": "here"}, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
