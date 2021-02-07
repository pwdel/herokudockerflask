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
      - 5002:5000
    env_file:
      - ./.env.dev
```
What the compose file does is defines the app's environment so that it can be reproduced anywhere.  The compose file defines the services that make up the app so they can be run together in an isolated environment.

The above yml file is doing the following:

1. Building the web service at / root directory, looking for the Dockerfile.
2. Running the server.py at 0.0.0.0
3. Attaching any volumes.
4. Running on port 5002, because we're already using port 5000 and 5001 for other projects.
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
Once we have a successful message, we should be able to connect to localhost:5002 and see the app.

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

```


2021-02-07T03:43:22.392969+00:00 heroku[web.1]: State changed from starting to crashed

2021-02-07T03:43:22.398916+00:00 heroku[web.1]: State changed from crashed to starting

2021-02-07T03:43:25.560637+00:00 heroku[web.1]: Starting process with command `python ./server.py`

2021-02-07T03:43:28.636000+00:00 app[web.1]:  * Serving Flask app "server" (lazy loading)

2021-02-07T03:43:28.636032+00:00 app[web.1]:  * Environment: production

2021-02-07T03:43:28.636078+00:00 app[web.1]:    WARNING: This is a development server. Do not use it in a production deployment.

2021-02-07T03:43:28.636158+00:00 app[web.1]:    Use a production WSGI server instead.

2021-02-07T03:43:28.636228+00:00 app[web.1]:  * Debug mode: off

2021-02-07T03:43:28.639911+00:00 app[web.1]:  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

2021-02-07T03:43:59.856613+00:00 heroku[router]: at=error code=H20 desc="App boot timeout" method=GET path="/" host=ancient-hollows-77002.herokuapp.com request_id=b582e826-5850-4e23-9d3d-1b068139548e fwd="207.153.48.94" dyno= connect= service= status=503 bytes= protocol=https

2021-02-07T03:44:26.158480+00:00 heroku[web.1]: Error R10 (Boot timeout) -> Web process failed to bind to $PORT within 60 seconds of launch

2021-02-07T03:44:26.205906+00:00 heroku[web.1]: Stopping process with SIGKILL

2021-02-07T03:44:26.301154+00:00 heroku[web.1]: Process exited with status 137

2021-02-07T03:44:26.420639+00:00 heroku[web.1]: State changed from starting to crashed

2021-02-07T03:44:26.837285+00:00 heroku[router]: at=error code=H10 desc="App crashed" method=GET path="/" host=ancient-hollows-77002.herokuapp.com request_id=a0c76b4b-e402-41d2-92a1-c12e79a9b61f fwd="207.153.48.94" dyno= connect= service= status=503 bytes= protocol=https

2021-02-07T03:44:27.233645+00:00 heroku[router]: at=error code=H10 desc="App crashed" method=GET path="/favicon.ico" host=ancient-hollows-77002.herokuapp.com request_id=1ab4e5d2-db5e-47ce-9930-ff2d96ff1ec8 fwd="207.153.48.94" dyno= connect= service= status=503 bytes= protocol=https


```


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




## Other Notes to Add

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