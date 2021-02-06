# Heroku Docker Flask

## Objective

To deploy a Flask App on Heroku using a Docker image.

## Past Work

* Previously, I had built a Flask app and deployed to Heroku using just regular virtualenv and Anaconda, as discussed [here](https://github.com/LinkNLearn/homedataflask).
* I also worked with deploying [Docker on Lubuntu 20](https://github.com/pwdel/dockerlubuntu).

## Software Planning

### Local Development



1. Use Docker Compose to define local environment. ```docker-compose.yml```
2. Spin up docker-compuse container.
3. Check to ensure app is working.
4. Push to Heroku

### Deployment

Heroku documentation recommends something called, "Container Registry & Runtime (Docker Deploys)," which I don't quite understand.

1. Install Heroku CLI
2. Install Heroku Container Registry
3. ?

## References

* [Basic Tutorial](https://www.youtube.com/watch?v=I5pYKXnzIWY)
* [Deploying with Docker](https://devcenter.heroku.com/categories/deploying-with-docker)
* [Local Development with Docker Compose](https://devcenter.heroku.com/articles/local-development-with-docker-compose)
* [Container Registry and Runtime](https://devcenter.heroku.com/articles/container-registry-and-runtime)