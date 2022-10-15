# Product helper app

This is an application for posting cooking recipes and chearing them to other people.
Here you can: 
- Add you own recipes.
- Make other recipes like yours favorite or add then in shopping cart.
- Take all ingredients from shopping cart recipes in txt file (you can print it and go buy them ^ _ ^)
## Required packages and programms 
 - > Docker with docker-compose
## How install and run
- Download all from git repository:
	- > git clone git@github.com:DevRomFromDom/foodgram-project-react.git
- Go in root of downloaded packege and in infra directory.
	- > cd  foodgram-project-react/infra
- Create .env file inside this folder and add folowed content:
	- > DB_ENGINE=django.db.backends.postgresql # We are using Posgres 
	- > DB_NAME=postgres # Name for db
	- > POSTGRES_USER=postgres # Login for db
	- > POSTGRES_PASSWORD=123456789 # Password for db
	- > DB_HOST=db # Name for db docker containner
	- > DB_PORT=5432 # Database port
	- > SECRET_KEY = 'super%difficult%key%1233456789'  # Your own key
	- > ALLOWED_HOSTS = ['*']
	- > DEBUG = False
- Build full app from docker images:
	- > docker-compose up -d --build
- Make migrations, load ingredients and load static: 
	- > docker-compose exec backend python manage.py migrate 
	- > docker-compose exec backend python manage.py update
	- > docker-compose exec backend python manage.py collectstatic --no-input
	  
	Create superuser with:
	- - > docker-compose exec backend python manage.py createsuperuser 
## Working URLs
 - > http://localhost/admin/ - admin page
 - > http://localhost/signin/ - app page

## Created by: 
- [Роман Каменских](https://github.com/DevRomFromDom)

![example workflow](https://github.com/DevRomFromDom/product_helper/actions/workflows/product_helper.yml/badge.svg)

## URLs to connect to cloud:
 - > http://84.201.136.98/signin
 - > http://84.201.136.98/recipes
 - > http://84.201.136.98/admin