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
