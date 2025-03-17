# Deployment

Some information on how to deploy the website - currently it is deployed on a temporary heicloud VM.

## Production deployment

Production docker container images are automatically built by CI.
Before running them, the location of the data directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker compose.yml.

For example the current test deployment on heicloud looks like this:

```
MONDEY_SSL_CERT="/etc/letsencrypt/live/mondey.lkeegan.dev/fullchain.pem"
MONDEY_SSL_KEY="/etc/letsencrypt/live/mondey.lkeegan.dev/privkey.pem"
```

### docker compose

To deploy the latest version on a virtual machine with docker compose installed,
download [docker-compose.yml](https://raw.githubusercontent.com/ssciwr/mondey/main/docker-compose.yml), then do

```
sudo docker compose pull && sudo docker compose up -d && sudo docker system prune -af
```

The same command can be used to update the running website to use the latest available docker images.

The current status of the running containers can be checked with

```
sudo docker compose ps
sudo docker compose logs
```

### SSL certificates

To generate SSL certificates for the domain `mondey.lkeegan.dev` from [Let's Encrypt](https://letsencrypt.org/) using [Certbot](https://certbot.eff.org/):

```
sudo docker run -it --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d mondey.lkeegan.dev
```

The certificates needs renewing every three months, which can be done manually using the same command. To automatically renew once a week you can use cron, e.g. `sudo crontab -e`, then add the following line:

```
0 0 * * 0 docker run -it --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d mondey.lkeegan.dev
```

To check that the production website SSL certificates are configured correctly:

https://decoder.link/sslchecker/mondey.lkeegan.dev/443

### Give users admin rights

To make an existing user with email `user@domain.com` into an admin, modify the users database, e.g.

```
sqlite3 db/users.db
sqlite> UPDATE user SET is_superuser = 1 WHERE email = 'user@domain.com';
sqlite> .quit
```
