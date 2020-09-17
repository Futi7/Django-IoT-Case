# SIMPLE DEVICE MANAGEMENT API WITH DJANGO REST FRAMEWORK
This API aims to add and manage devices and get log informations.
## Requirements
- Python 3.7
- Django (3.0.7)
- Django REST Framework


## Installation
For installing Python on Ubuntu:
```
	sudo apt update
    sudo apt install python3.7
    
```


For installing Python on Mac OS X:
```
	brew install python
```

Run below code in project directory from shell.
```
	pip instal -r requirements.txt
```
For those who has multiple python version i recommend you to use:
```
	pip3 instal -r requirements.txt
```
## Structure
Visit /api/ for API structure

## Use
Before you run the project run below commands.
```
python manage.py migrate
python manage.py createsuperuser
```
After you created super user you can simply run

```
	python manage.py runserver
```
Only authenticated users can use the API services, for that reason if you try:
```
	http://127.0.0.1:8000/api/device-list/
```
you'll get:
```
 {  "detail":  "Invalid username/password."  }
```
Use basic authentication from REST client with you r credentials or
simply login from browser(if you are using browser as client)

Follow the 'API Documentation' from /api/ for further usage info about the API.