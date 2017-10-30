## UniConnect - Project web application


Download the source code by using git:

```

git clone https://username@bitbucket.org/elec3609_group7/uniconnect.git
```

## Model Setup

```
$ pip install -r requirements.txt
$ python manage.py migrate
```

## Start web application

```
$ python manage.py runserver 0.0.0.0:8000
```

Go to `127.0.0.1:8000`

### REST API use

type url:
```
http://127.0.0.1:8000/postapi/
```
to create a post

```
http://127.0.0.1:8000/postapi/id
```
to view a post detail

```
http://127.0.0.1:8000/userapi/
```
to create a user (only for Admin)

```
http://127.0.0.1:8000/userapi/id
```
to view a user detail

```
http://127.0.0.1:8000/profileapi/
```
to create a profile for user

```
http://127.0.0.1:8000/profileapi/id
```
to view a user profile

```
http://127.0.0.1:8000/commentapi/
```
to create a comment

```
http://127.0.0.1:8000/commentapi/id
```
to view a comment
