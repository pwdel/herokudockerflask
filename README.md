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


### Create entrypoint.sh if Needed

* Created entrypoint.sh in the root folder, and modified Dockerfile to run this entrypoint.sh file, which might be useful to prevent the server from restarting if a sever.pid already exists.

The contents of entrypoint.sh, an exectuable, are the following:

```
#!/bin/bash
set -e

# Remove a potentially pre-existing server.pid for Rails.
rm -f /app/tmp/pids/server.pid

# Then exec the container's main process (what's set as CMD in the Dockerfile).
exec "$@"
```

### Use docker-compose.yml

Within docker-compose.yml, we put:

```
version: '3'
services:
  db:
    image: postgres:latest
    volumes:
      - ./tmp/db:/var/lib/postgresql/data
  web:
    build: .
    command: bash -c "rm -f tmp/pids/server.pid && bundle exec rails s -p 3000 -b '0.0.0.0'"
    volumes:
      - .:/myapp
    ports:
      - "3000:3000"
    depends_on:
      - db
```


### Docker Compose

* Next we run the container to ensure that it works. However, rather than use docker build we will use docker-compose.

```
docker-compose
```



## References

* [Basic Tutorial for Ruby on Rails on Medium](https://medium.com/better-programming/how-to-containerize-and-deploy-apps-with-docker-and-heroku-b1c49e5bc070)
* [Basic Tutorial on YouTube](https://www.youtube.com/watch?v=I5pYKXnzIWY)
* [Deploying with Docker](https://devcenter.heroku.com/categories/deploying-with-docker)
* [Local Development with Docker Compose](https://devcenter.heroku.com/articles/local-development-with-docker-compose)
* [Container Registry and Runtime](https://devcenter.heroku.com/articles/container-registry-and-runtime)
* [Build Docker Images on Heroku](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml)