# -*- coding: utf-8 -
#



"""
Settings for API and connectivity 
"""

#root url for application
API_ROOT = 'https://www.elmware.com'

#max number of times the app will retry a request due to lack of connectivity
MAX_CONNECTIVITY_RETRY = 3

#delay between failed API requests in seconds
API_RETRY_DELAY = 5

#sleep time while waiting for task from server in seconds
TASK_WAIT_SLEEP = 3

#Headers used for get requests
GET_HEADERS = {
    'Content-type': 'application/json'
}

POST_HEADERS = {
    'Content-type': 'application/json'
}