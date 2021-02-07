# Heroku Docker Flask

## Objective

To deploy a Flask App on Heroku using a Docker image.

## Past Work

* Previously, I had built a Flask app and deployed to Heroku using just regular virtualenv and Anaconda, as discussed [here](https://github.com/LinkNLearn/homedataflask).
* I also worked with deploying [Docker on Lubuntu 20](https://github.com/pwdel/dockerlubuntu).

## Software Planning

### Local Development

1. Use the basic Docker "hello world," app that we previously built mentioned above, run on local machine.
2. Check Dockerfile, ensure works for our new Heroku environment.
3. Crate entrypoint.sh if needed for Flask.
4. Use docker-compose.yml to describe different services on app which end up in different containers upon building.
5. Build the app, create the database if needed.
6. Double check that app works on port.

### Deployment to Heroku

1. Login to heroku via CLI, with container.
2. Create a new app.
3. Ensure resources provisioned on Heroku Dashboard, including environmental variables needed.
4. Double check that app works on endpoint.

### Updating and Changing App

After this point, the app can be further improved, updated and changed.

## Local Development

### Using Existing App

* So the first thing to do, which is quite easy, is simply copy the App and Dockerfile from [Docker on Lubuntu 20](https://github.com/pwdel/dockerlubuntu).

* I changed the working directory WORKDIR to /app and put the Dockerfile in the root directory for cleanliness.

* We had to change multiple files to utilize /app to ensure this worked.

```
docker build -t herokuflask_test .
```

After building we see the following:

| REPOSITORY       | TAG    | IMAGE ID     |
|------------------|--------|--------------|
| herokuflask_test | latest | 84b560d4bacd |

We then run:

```
sudo docker run -d -p 5000:5000 herokuflask_test
```
However, we noted when running this we getr:

```
failed: port is already allocated.
```
So, we have to change the port on the command.

```
sudo docker run -d -p 5001:5000 herokuflask_test
```

| CONTAINER ID | IMAGE            | COMMAND              | PORTS                  | NAMES      |
|--------------|------------------|----------------------|------------------------|------------|
| 87386cc45475 | herokuflask_test | "python ./server.py" | 0.0.0.0:5001->5000/tcp | silly_bose |

When we visit "localhost:5001" we get the message as expected, "Hello World!"  However, how can we be sure this isn't just the other app running?  We need to slightly modify the code and re-run or re-build everything to ensure things are working properly.

Instead of, "Hello World!" we added the message, "Hello World Little Dude!" and then re-built and re-ran the app, as follows:

1. Modified the Code.
2. Stopped the container at port 5001 with "docker stop CONTAINER_ID"
3. Removed the container at port 5001 with "docker rm CONTAINER_ID"
4. Removed the image with, "sudo docker rmi -f IMAGE_ID" 

After running the image at localhost:5001 once again, we get the message: "Hello World Little Dude!" 

### Use docker-compose.yml

Within docker-compose.yml, in the project root we put:

```
version: '3.8'

services:
  web:
    build: ./
    command: python server.py run -h 0.0.0.0
    volumes:
      - ./app/:/src/
    ports:
      - 5000:5000
    env_file:
      - ./.env.dev
```
What the compose file does is defines the app's environment so that it can be reproduced anywhere.  The compose file defines the services that make up the app so they can be run together in an isolated environment.

The above yml file is doing the following:

1. Building the web service at / root directory, looking for the Dockerfile.
2. Running the server.py at 0.0.0.0
3. Attaching any volumes.
4. Originally we ran on port 5002, and we later switched back to port 5000.  We were running on port 5002, because we're already using port 5000 and 5001 for other projects.
5. Reference env file, which we need to create.

So we create a .env.dev file in the project root to store environmental variables for development.

```
FLASK_APP=app/server.py
FLASK_ENV=development
```
We then build the image.  We have to ensure we have docker-compose installed, following [these instructions](https://docs.docker.com/compose/install/).

```
docker-compose build
```

We run the following to run the entire app, in detached mode. This builds, (re)creates, starts, and attaches to containers for a service.

```
docker-compose up -d
```
Once we have a successful message, we should be able to connect to localhost:5002 (or localhost:5000 after switching back) and see the app.

If this didn't work then you can run the command to look at log errors: "sudo docker-compose logs"

### Logging Into Heroku

In order to login to Heroku and deploy from the command line, we must first install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

Then you login with, "heroku login" and follow the prompt to open a browser.

Login to the Heroku docker registry via:

```
docker login --username=_ --password=$(heroku auth:token) registry.heroku.com
```

Then you can create an app with: "heroku create"

Next, you can push the container to the web as follows:

```
sudo heroku container:push web --app ancient-hollows-77002
```

You should get a success message that says, "Your image has been successfully pushed. You can now release it with the 'container:release' command."

Then you can do a release, as follows:

```
heroku container:release web --app ancient-hollows-77002
```

You can then check:

https://ancient-hollows-77002.herokuapp.com

To ensure that the app has been deployed.

### Debugging the Deployment

Moving from development to production is always a challenge.  Different environments causing mix-ups, failure to set environmental variables, and unforseen errors abound when moving from .dev to .prod.

After pushing our dockerized app to prod above, right away we see a few errors, and a failure to serve.

#### Serving on Port 5000

We see an error:

```
2021-02-07T03:44:26.158480+00:00 heroku[web.1]: Error R10 (Boot timeout) -> Web process failed to bind to $PORT within 60 seconds of launch
```
Basically, this is because we didn't set the Port to 5000 within the flask app itself. We can fix this by two additions to the server.py app.

```
from flask import Flask
server = Flask(__name__)
# set the port to 5000 for Heroku
port = int(os.environ.get("PORT", 5000))

@server.route("/")
def hello():
    return "Hello World, Little Dude!"

if __name__ == "__main__":
# set port = port for Heroku
   server.run(host='0.0.0.0',port=port) 
```

Upon changing the code, we need to rebuild our Docker Image and re-run the container. Don't forget that you have to delete the old container as well.

Fortunately, I created a shell script to help us stop and remove all Docker containers and images, as well as other useful rebuild scripts which can be found [here](https://github.com/pwdel/dockerlubuntu/tree/main/lib).

After getting rid of what we need to, we then run:

```
sudo docker-compose build 

sudo docker-compose up -d
```

Upon running this, we now see the error "web_1  | NameError: name 'os' is not defined" - therefore, we have to add, "import os" within the server.py file.

Upon importing os, we are able to run the Docker container.

#### Using a Production WSGI Server

We also see another error:

```
2021-02-07T03:43:28.636078+00:00 app[web.1]:    WARNING: This is a development server. Do not use it in a production deployment.

2021-02-07T03:43:28.636158+00:00 app[web.1]:    Use a production WSGI server instead.
```
So right away, we need to make sure that we set things to production, and this means essentially working with multiple environments, which means setting up a docker-compose.prod.yml file.

```
version: '3.7'

services:
  web:
    build: ./services/web
    command: gunicorn --bind 0.0.0.0:5000 manage:app
    ports:
      - 5000:5000
    env_file:
      - ./.env.prod
#    depends_on:
#      - db
#  db:
#    image: postgres:12-alpine
#    volumes:
#      - postgres_data:/var/lib/postgresql/data/
#    env_file:
#      - ./.env.prod.db

#volumes:
#  postgres_data:
```
Note in the above file, we're commenting out the volume and database information for now because we don't need it.

With the above in place, we can create our .env.prod file:

```
FLASK_APP=app/server.py
FLASK_ENV=production
DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_prod
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
```
We then bring down the containers that we had activated earlier:

```
sudo docker-compose down
```

...and we build the new production images using the prod.yml:

```
docker-compose -f docker-compose.prod.yml up -d --build
```

Of course, if we run this, then we get an error, 

"ERROR: for web  Cannot start service web: OCI runtime create failed: container_linux.go:349: starting container process caused "exec: \"gunicorn\": executable file not found in $PATH: unknown"

This is because we never included gunicorn, the [WSGI HTTP server Gunicorn](https://gunicorn.org/) in the requirements.txt file.

When we want to add a database, we will later also install [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) and [psycopg2](https://pypi.org/project/psycopg2/), for the database.

```
Flask==1.1.2
Flask-SQLAlchemy==2.4.1
gunicorn==20.0.4
```

Trying again...we do docker-compose build and docker-compose up and see that a web service gets started.  We see that this web service has an output on the command line, and upon visiting localhost:5000 we see a result.  Each time we visit localhost:5000 we get an addiontal message service on our local command line:

```
web_1  | 172.19.0.1 - - [07/Feb/2021 18:50:40] "GET / HTTP/1.1" 200 -
```
We can also take a look at our processes.

| CONTAINER ID | IMAGE                 | COMMAND                | CREATED       | STATUS        | PORTS                  | NAMES                   |
|--------------|-----------------------|------------------------|---------------|---------------|------------------------|-------------------------|
| cacee7836f5b | herokudockerflask_web | "python server.py ru…" | 9 minutes ago | Up 23 seconds | 0.0.0.0:5000->5000/tcp | herokudockerflask_web_1 |

Then, we can run the following to push this to Heroku again.  First, we log into the docker container registry:

```
sudo docker login --username=_ --password=$(heroku auth:token) registry.heroku.com
```

Push the container to the web as follows:

```
sudo heroku container:push web --app ancient-hollows-77002
```

You should get a success message that says, "Your image has been successfully pushed. You can now release it with the 'container:release' command."

Then you can do a release, as follows:

```
heroku container:release web --app ancient-hollows-77002
```

We should get a message that says, "Releasing images web to ancient-hollows-77002... done"

Upon successful release, we can visit our URL live on the web at [https://ancient-hollows-77002.herokuapp.com/](https://ancient-hollows-77002.herokuapp.com/) to view the message, "Hello World Little Dude!"

#### How Does the Heroku container:push Command Know Which Container to Use?

Basically, when you run, ```heroku container:push web``` [per the documentation](https://devcenter.heroku.com/articles/container-registry-and-runtime) the heroku cli is building pushing an image to a container registry, where it is getting built.  The container is then, "released" from that registry.

https://blog.heroku.com/container-registry-and-runtime

How does heroku container:push know which image to use?

| REPOSITORY                                    | TAG             | IMAGE ID     | CREATED        | SIZE  |
|-----------------------------------------------|-----------------|--------------|----------------|-------|
| herokudockerflask_web                         | latest          | b827eadbbef7 | 22 minutes ago | 135MB |
| registry.heroku.com/ancient-hollows-77002/web | latest          | b827eadbbef7 | 22 minutes ago | 135MB |
| python                                        | 3.9-slim-buster | d5d352d7d840 | 5 days ago     | 114MB |


Basically within the command:

```
sudo heroku container:push web --app ancient-hollows-77002

```
...the term, --app is the name of our app.  If our app was named something else, like, my_app or my_widget_thingy, then we would put --my_app or --my_widget_thingy.

### Create entrypoint.sh if Needed


* At this point, the entrypoint.sh file is not needed, because there isn't any additional containers with services added, such as a database - it's just a simple app that prints, "Hello World Little Dude!"  However, we can create a placeholder entrypoint and enter in some of the recommended items that would normally exist.
* Created entrypoint.sh in the root folder, and modified Dockerfile to run this entrypoint.sh file, which might be useful to prevent the server from restarting if a sever.pid already exists.

The contents of entrypoint.sh, an exectuable, are the following:

```
#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py create_db

exec "$@"
```

## Other Things to Google Related to this Project

* Environmental Variables on Docker

## References

*[Containerize your Python Flask app using Docker and Deploy to Heroku](https://medium.com/@ksashok/containerise-your-python-flask-using-docker-and-deploy-it-onto-heroku-a0b48d025e43)
* [Compose File Reference](https://docs.docker.com/compose/compose-file/)
* [Dockerizing Flask with Postgres, Guinicorn and Nginx](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/)
* [Basic Tutorial for Ruby on Rails on Medium](https://medium.com/better-programming/how-to-containerize-and-deploy-apps-with-docker-and-heroku-b1c49e5bc070)
* [Basic Tutorial on YouTube](https://www.youtube.com/watch?v=I5pYKXnzIWY)
* [Deploying with Docker](https://devcenter.heroku.com/categories/deploying-with-docker)
* [Local Development with Docker Compose](https://devcenter.heroku.com/articles/local-development-with-docker-compose)
* [Container Registry and Runtime](https://devcenter.heroku.com/articles/container-registry-and-runtime)
* [Build Docker Images on Heroku](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml)
* [Writing a Script to Remove and Restart Docker Images](https://stackoverflow.com/questions/41322541/rebuild-docker-container-on-file-changes)