from octopie.api import GitHubAPI
from octopie.api import APIError

api_client = GitHubAPI()
result = {}
try:
    print api_client.users.get('stevenc81')
    print api_client.getHeaders()
except APIError as e:
    print e