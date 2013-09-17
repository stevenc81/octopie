=======
octopie
=======

Python API client for GitHub APIv3

## Installation

### To Run
    pip install octopie

### To Develop
    Nothing specific now

## Usage
    import octopie

    client = octopie.GitHubAPI()

    try:
       result = client.search.users.get(q='language:python')
    except APIError as e:
        print e

In case of having variables for an API call. For example:

    GET /repos/:owner/:repo/collaborators

The octopie for above example will be:

    owner = 'steven'
    repo = 'octopie'
    result = api_client.repos.__getattr__(owner).__getattr__(repo).collaborators.get())