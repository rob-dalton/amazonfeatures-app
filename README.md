# Amazonfeatures App
This repo contains the frontend Flask application for `amazonfeatures`. It's a Python 2.7 based app served using `uwsgi` on Ubuntu Xenial 16.04. In order to run it, you must have a local MongoDB instance running with a `reviews` database containing processed reviews.

You can see a live demo of the app here: [https://amazonfeatures.robdalton.me](https://amazonfeatures.robdalton.me)

For DB setup and review processing, please see here: [amazonfeatures-review-processing](https://github.com/rob-dalton/amazonfeatures-review-processing).

For how to deploy the app, please see here: [How to Serve a Web App With NGINX, uWSGI and Flask. And Why You'd Want to.](https://robdalton.me/how-to-serve-a-web-app-with-nginx-uwsgi-and-flask-and-why-youd-want-to/)