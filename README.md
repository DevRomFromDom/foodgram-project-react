# Product helper app

This is an application for posting cooking recipes and chearing them to other people.
Here you can: 
- 1) Add you own recipes.
- 2) Make other recipes like yours favorite or add then in shopping cart.
- 3) Take all ingredients from shopping cart recipes in txt file (you can print it and go buy them ^ _ ^)
## Required packages and programms 
 - > Docker with docker-compose
## How install and run
- 1) Download all from git repository:
	- > git clone git@github.com:DevRomFromDom/foodgram-project-react.git
- 2) Go in root of downloaded packege and in infra directory.
	- > cd  foodgram-project-react/infra
- 3) Create .env file inside this folder and add folowed content:
-- DB_ENGINE=django.db.backends.postgresql # We are using Posgres 
--  DB_NAME=postgres # Name for db
-- POSTGRES_USER=postgres # Login for db
-- POSTGRES_PASSWORD=123456789 # Password for db
-- DB_HOST=db # Name for db docker containner
-- DB_PORT=5432 # Database port
-- SECRET_KEY = 'super%difficult%key%1233456789'  # Your own key
-- ALLOWED_HOSTS = ['*']
-- DEBUG = False
- 4) Build full app from docker images:
	- > docker-compose up -d --build
- 5) Make migrations, load ingredients and load static: 
	- > docker-compose exec backend python manage.py migrate 
	- > docker-compose exec backend python manage.py update
	- > docker-compose exec backend python manage.py collectstatic --no-input
	  
	Create superuser with:
	- - > docker-compose exec backend python manage.py createsuperuser 
## Working URLs
 -> http://localhost/admin/ - admin page
 -> http://localhost/signin/ - app page

## Created by: 
- [Роман Каменских](https://github.com/DevRomFromDom)

![example workflow](https://github.com/DevRomFromDom/yamdb_final/actions/workflows/product_helper.yml/badge.svg)