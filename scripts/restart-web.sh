docker-compose stop web
docker-compose build web
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
docker-compose up -d --no-deps web
