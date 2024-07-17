# AI Blog Test Task | STARNAVI
## Task Description
_Create a simple API for managing posts and comments with AI moderation and automatic response functionality. The API should be developed using FastAPI and Pydantic._

- This project was created with `Django, Django-Ninja` technologies as these were few of allowed technologies. 
- For token-based authentication was used `Django-Ninja-JWT` which is based on `Simple JWT` python library.
- For AI functionality was used `Google Generative Ai` python library to work with `Gemini`.
- Database used `SQLite` since we don't need more for testing purpose, but it can easily be changed at any time thanks to django structure.

### Implemented Functionality
1. User registration;
2. User login;
3. API for managing posts;
4. API for managing comments;
5. Check posts or comments for profanity, insults, etc., at the time of creation, and block such posts or comments.
6. Analytics on the number of comments added to posts over a certain period. Example URL: /api/comments-daily-breakdown?date_from=2020-02-02&date_to=2022-02-15. The API should return daily aggregated analytics for each day, showing the number of created comments and the number of blocked comments.
7. Automatic response function for comments if the user has enabled it for their posts. The automatic response should not happen immediately but after a period set by the user. The response should also be relevant to the post and the comment being responded to.

## Local Project Setup
1. Install Python from https://www.python.org/
2. Install Redis: https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/
3. In `/ai-blog/` root directory create python environemnt with command: `python -m venv env`
4. Activate created environment. (https://docs.python.org/3/library/venv.html)
5. Install requirements with command: `pip install -r requirements.txt`
6. Create `.env` file in root directory and create there 2 variables: `SECRET_KEY = u#d-6mzeich*l$18qv46eeik49u__w)9-k(r=3-4ik^2=61&al`, `GEMINI_API_KEY = your gemini api key`. Provided SECRET_KEY use only for testing purpose.
8. Migrate django models to database with command: `python manage.py migrate`
9. Open 3 separate terminals. One of them we need to run django server. Two other we need for celery workers.
10. In first terminal type: `python manage.py runserver` - to start server locally. Default port is: `8000`. You should already be able to acces http://127.0.0.1:8000/api/docs
11. In second terminal type: `celery -A ai_blog worker -Q default -n dynamic_pt_node -l info -E`. This will start celery worker on redis.
12. In third terminal type: `celery -A ai_blog beat -l info`. This will start celery scheduler.

## Docker
1. Windows:
    - Install Docker Desktop: https://www.docker.com/products/docker-desktop/
    - Open downloaded program
    - Verify docker installation with command: `docker-compose -v`
    - In project's root run command: `docker-compose build` to build a docker image
    - After build successfully completed run command: `docker-compose up`

2. Linux:
    - Install Docker: https://docs.docker.com/engine/install/ubuntu/#installation-methods
    - Install docker compose plugin: `sudo apt-get install docker-compose-plugin`
    - In project's root run command: `docker compose build` to build a docker image
    - After build successfully completed run command: `docker compose up`

## Known Issues
### Gemini
Gemini has a free plan, but it is not accesible in many countries, particularly in Europe. You can check your country here: https://ai.google.dev/gemini-api/docs/available-regions#unpaid-tier-unavailable.
If you don't have access to free plan, you can use VPN to change your location to one of supported countries - recieve a key and then you need to test the project with VPN turned on.

### Redis on Windows
Redis could be a bit annoying to use on Windows localy that's why Docker is recommended or you can always use Linux. To run project localy you will need WSL (windows subsystem linux). When using WSL don't forget that you need to type `celery` commands inside of project root folder.
