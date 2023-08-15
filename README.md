## Sport APP

### Setup

1) Activate the virtual envirnoment
```
source your-env/bin/activate
```

2) Install the requirements
```
pip freeze -r requirements.txt
```

3) Migrate the migrations by running this command
```
python manage.py migrate
```

4) Run app
```
python manage.py runserver
```


### Run with docker

1) Build image 
```
docker build -t my-django-app .
```
It takes some time.

2) Run cmd
```
docker run -p 8000:8000 my-django-app
```

Then you can paste the http://127.0.0.1:8000/ on browser


Note: Before running with docker you need to run the migrations