# French regions
Simple API to get infos on french regions

Live API here -> https://french-reg.herokuapp.com/api/regions/
With pagination: https://french-reg.herokuapp.com/api/regions/?page=1

## Requirements
- Python 3.7.5 or higher
```bash
pip3 install virtualenv
virtualenv venv
source venv/bin/activate # . venv/bin/activate
pip3 install -r requirements.txt
```

## Create database
There is already a db on the repo for convenience but, if you want to start from scratch and populate your own sqlite db well feel free to do so by typing this command.
```
python3 db_create.py
```

## Run the server locally
```
python3 server.py
```
The API can be fetched here -> http://localhost:5000/api/regions/
The limit is 10 regions per response, you can get more result with the pagination
->  http://localhost:5000/api/regions/?page=1
