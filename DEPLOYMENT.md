# Deployment

Some information on how to deploy the website - currently it is deployed on a temporary heicloud VM.

## Production deployment

Production docker container images are automatically built by CI.
To deploy the latest version on a virtual machine with docker compose installed,
download [docker-compose.yml](https://raw.githubusercontent.com/ssciwr/mondey/main/docker-compose.yml), then do

```
sudo docker compose pull
sudo docker compose up -d
```

The location of the database directory, image files directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker-compose.yml.

TODO: document these options

The current status of the containers can be checked with

```
sudo docker compose ps
sudo docker compose logs
```

To update the running website to the latest version:

```
sudo docker compose pull && sudo docker compose up -d && sudo docker system prune -af
```

### Give users admin rights

To make an existing user with email `user@domain.com` into an admin, modify the users database, e.g.

```
sqlite3 db/users.db
sqlite> UPDATE user SET is_superuser = 1 WHERE email = 'user@domain.com';
sqlite> .quit
```
