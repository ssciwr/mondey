# Deployment

Some information on how to deploy the website - currently it is deployed on a temporary heicloud VM.

A FAQ section is included at the end.

## Production deployment

Production docker container images are automatically built by CI.
Before running them, the location of the data directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker compose.yml.

For example the current test deployment on heicloud looks like this:

```
MONDEY_SSL_CERT="/etc/letsencrypt/live/mondey.de/fullchain.pem"
MONDEY_SSL_KEY="/etc/letsencrypt/live/mondey.de/privkey.pem"
DEEPL_API_KEY=abc123
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

To generate SSL certificates for the domain `mondey.de` from [Let's Encrypt](https://letsencrypt.org/) using [Certbot](https://certbot.eff.org/):

```
sudo docker run -it --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d mondey.de
```

The certificates needs renewing every three months, which can be done manually using the same command.
To automatically renew once a week you can use cron, e.g. `sudo crontab -e`, then add the following line:

```
0 0 * * 0 docker run --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d mondey.de
```

To check that the production website SSL certificates are configured correctly:

https://decoder.link/sslchecker/mondey.de/443

### Give users admin rights

To make an existing user with email `user@domain.com` into an admin, modify the users database, e.g.

```
docker exec -it $(docker ps | grep usersdb-1 | awk '{print $1}') bash
psql -U postgres -d users
UPDATE "user" SET is_superuser = true WHERE email = 'user@domain.com';
```
This only needs to be done for the first admin user in a new deployment,
as they can then log in and give other users admin rights from the admin interface.

### Internationalization

All text on the website is translated into multiple languages, and the translations can be edited from the admin interface.
In the frontend code, all user-facing text is defined (with placeholder german texts) in [frontend/src/lib/translations.ts](https://github.com/ssciwr/mondey/blob/main/frontend/src/lib/translations.ts).
When the website is loaded by a user, the translations that were made in the admin interface for all of these texts are downloaded from the server.

_Note: When new text is added to [frontend/src/lib/translations.ts](https://github.com/ssciwr/mondey/blob/main/frontend/src/lib/translations.ts),
and the deployed website has been updated,
the translations for this new text need to entered using the admin interface.
Until this is done the new text will not be visible in the deployed website!_

### DeepL API key

The automatic translation buttons in the admin interface use the DeepL API to translate text.
To use this feature, an API key is needed which can be set in the `.env` file where the docker-compose.yml is located.
The DeepL API Free plan currently offers 500,000 characters per month for free, which should be sufficient (a credit card is required at sign up but is not charged).

### Emails

#### SMTP

The emails sent from the website are sent using SMTP.
The SMTP server and credentials can be configured by setting these environment variables:

- `SMTP_HOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

By default this is set to use the postfix send-only docker image included in the docker compose,
but if you have an email account you wish to use instead you can set these SMTP server and credentials accordingly.

The postfix image will by default try to send emails directly using port 25.
Some ISPs and networks block this port, but may provide a SMTP relay service that should be used instead.
This can be configured by setting these environment variables:

- `RELAYHOST`
- `RELAYHOST_USERNAME`
- `RELAYHOST_PASSWORD`

Currently the website is hosted on a heicloud VM, which uses the heidelberg university network SMTP relay (`relays.uni-heidelberg.de:25`, no username/password) to send emails.

#### DNS

In order to avoid emails being sent to spam, there are several DNS security features that should be configured.

**SPF record**

- adds the IP address of the mail server(s) allowed to send emails from this website to the DNS info
- if using a commercial mail sending service they will provide this info
- for heidelberg uni
  - we can look it up: https://mxtoolbox.com/SuperTool.aspx?action=spf%3auni-heidelberg.de&run=toolpage
  - for the temporary namecheap sub-domain mondey.de:
    - Type: `TXT Record`
    - Host: `mondey`
    - Value: `v=spf1 ip4:129.206.100.212 ip4:129.206.119.212 ip4:129.206.100.213 include:spf.protection.outlook.com mx -all`
- check the changes worked with e.g. https://dmarcian.com/spf-survey/?domain=mondey.de

**DKIM**

- adds a public key to the DNS info
- sent emails are signed with this key by the email server
- if using a commercial mail sending service they will provide this info
- for heidelberg uni
  - postfix docker image will generate DKIM keys if not already present with selector `mail`
  - copy the generated dns entry from opendkim-keys/mondey.de.txt
    - note remove any quotes and newlines and spaces after `p=`!
  - for the temporary namecheap sub-domain mondey.de:
    - Type: `TXT Record`
    - Host: `mail._domainkey.mondey`
    - Value: `v=DKIM1; h=sha256; k=rsa; s=email; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1s+IQlEUKtJ6Gt2/h5x7M949Vdmue7A5al2asflVXTvw7me8OCCsYx2FaWjLDPNpXHxEhUVYqJQKUTyvZnpjIxBXg86hSnBaO0YUQXsE2pz4jNt9BOEGhKACc47DkJEg3XOcJqf7JnrWkOELLnWS2RKzDUZ3e1/5cjolvtJuMEQFay1EITCamCJOUsA+gZ12XC4j10k3aT/MPxhOG9Wj8VhD7eLHI0QV1XRD7DrzO7EyA9R/Eve/l1FGx5CzuNIjKhmb1FVGiepqkPZgooDs9hxXCElQVqP6CQFyDRY64SiV1kTfVVSvL1N5PiU2BxP2IKKaXvn4/H55Zjz5j1+sQIDAQAB`
- to check this entry is valid before using: e.g. https://dmarcian.com/dkim-validator/
- check the changes worked with e.g.: e.g. https://dmarcian.com/dkim-inspector/?domain=mondey.de&selector=mail

**DMARC record**

- DMARC policy indicates valid spf/dkim and what to do if not
- if using a commercial mail sending service they will provide this info
- for the temporary namecheap sub-domain mondey.de:
  - Type: `TXT Record`
  - Host: `_dmarc.mondey`
  - Value: `v=DMARC1; p=reject`
- check the changes worked with e.g. https://dmarcian.com/dmarc-inspector/?domain=mondey.de

**Testing**

Some resources to check if all this worked:

- https://www.mail-tester.com/
- https://easydmarc.com/tools/domain-scanner?domain=mondey.de
- https://mxtoolbox.com/SuperTool.aspx
- https://www.mail-tester.com/spf-dkim-check

### Database

#### Modifying the database

To modify the database, you can connect to the running postgres database in the `mondeydb` container and then enter an SQL command:

```
docker exec -it $(docker ps | grep mondeydb-1 | awk '{print $1}') bash
psql -U postgres -d mondey
```

#### sqlite to postgres migration

Notes on the (one-off) process used to migrate the sqlite databases to postgres in production:

- temporarily add `- ./db:/db` to the mondeydb and usersdb volumes in docker-compose.yml to mount the db folder
- recreate the containers (this will also create the postgres databases and tables): `docker compose up -d --force-recreate`
- ssh into the `mondeydb` docker container: `docker exec -it $(docker ps | grep mondeydb-1 | awk '{print $1}') bash`
- install pgloader: `apk update && apk add pgloader`
- import the data from sqlite without modifying any tables: `pgloader --with "data only" sqlite:///db/mondey.db pgsql://postgres@127.0.0.1/mondey`
- do the same for the usersdb container:
  - `docker exec -it $(docker ps | grep usersdb-1 | awk '{print $1}') bash`
  - `apk update && apk add pgloader`
  - `pgloader --with "data only" sqlite:///db/users.db pgsql://postgres@127.0.0.1/users`

#### postgres database backups

The docker-compose.yml file includes [docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local)
which is configured to make daily backups of the mondey and users databases in the `POSTGRES_DATA_PATH_MONDEY_BACKUPS` and `POSTGRES_DATA_PATH_USER_BACKUPS`
directories, which by default are `db_backups/mondey` and `db_backups/users` if not set explicitly.
Backups are kept for the last 7 days, one per week for the last 4 weeks, and one per month for the last 6 months, and are stored in folders named accordingly.
To restore the most recent mondeydb backup:

```
zstdcat db_backups/mondey/last/mondey-latest.sql.gz | docker exec -i $(docker ps | grep mondeydb-1 | awk '{print $1}') psql --username=postgres --dbname=mondey
```

And similarly for the usersdb:

```
zstdcat db_backups/users/last/users-latest.sql.gz | docker exec -i $(docker ps | grep usersdb-1 | awk '{print $1}') psql --username=postgres --dbname=users
```


# Frequently Asked Questions
## Application

**Is Mondey.de running in a heiCLOUD VM? Which are the current specs of it (type of VM, volumes types and sizes)?**

Yes. The specs are: Linux VM with 2 CPUS, 4GB RAM, 30GB storage

**What are the recommended CPU, RAM, and storage requirements to run mondey?**

The storage usage should be regularly checked. Images are stored on the application, but in the main use cases not typically used at time of writing. Most other data is text or numerical.

The main storage requirement is for the database and logs. Currently the databases use ~150mb (but this is mostly caching, the actual db is only a few mb), the logs are configured to use ~1.2gb max (but that can be set to any desired value), and the database backups are < 5mb.

**Does it run as a single service or are there multiple components (e.g., web server + database)? (I have seen the docker compose file has several services configured)**

Multiple docker services are ran via a coordinating Docker compose file.

**Which operating system is currently used in production (e.g., Ubuntu 22.04, Debian, etc.)?**

The operating system should not really matter as the Dockerfiles should each specify their needed base image and there are no specific extra requirements (e.g. no GPU/nvidia). Ubuntu 24.04 is currently used in production.

**Is it running in a container (Docker/Podman) or directly on the OS?**

The docker compose command should be launched directly from the VM, which starts a number of docker containers.

**Are there any other services it integrates with (e.g., message brokers, cloud storage, mail, external databases)?**

Yes, the email server. Currently it is connected to the university email relay. There is also the Deepl API for translations, which is detailed in ./DEPLOYMENT.md

**How much load (CPU %, memory usage, disk I/O) does it normally use?**

As a FastAPI and Svelte 5 project, usage should not be much, mostly peaking during things like big data changes.
With current use the cpu load is minimal, 500mb ram

**How is it backed up now?**

There are two databases. They both back up onto the same machine via the Docker Compose arguments to their docker services (BACKUP_ON_START=TRUE etc). These can be configured to adjust the back up interval and keep period, and to back up to a different machine. Currently the backups are stored on the same VM that the website is running on.

**How do admins access and modify the website to make little changes (like Igor is doing nowadays)?**

The process is to create code change commits related to issues. When tests pass with those changes, a PR can be merged into the main branch. There, if the tests pass, the CI will rebuild the images that running production instances pull from (every night at 1AM UTC because of "watchtower"), updating them that way. Manual updates are also possible, detailed below in another answer.

## Storage

**How much disk space is currently used (application + data)?**

Disk space used: a few hundred mb

**How fast does the data grow (GB/day or per month)?**

This is hard to predict until seeing regular usage. However, a thousand children of the type imported so far (without images) comes to meaningfully less than 500mb. So for up to 10,000 children, < 5000mb is likely necessary. For 100,000 children, < 50GB.

**What kind of storage performance is required (HDD sufficient? SSD better?)?**

Besides statistics calculations, there are not many database intensive uses or queries. SSD would be preferred, but not necessary. If using HDD, you may wish to consider adding more indexes.

**Are there backups currently implemented?**

Yes, back ups of the databases run via dedicated docker services, and are saved locally only at present. Backups are stored in the db_backups/mondey and db_backups/users directories

**How should we back up the data?**

This is up to you, you could set up a second location to back up to, or change the interval/keep duration of back ups.

## Network

**Which ports/services need to be open?**

Port 80 and 443 should be open in both directions for the web interface, and whatever port the smtp server uses for sending should be open for egress (25 for the heidelberg relay host currently in use). You'll probably also need to open port 22 for ssh access to administer the VM.

**Are there any firewall or security group requirements?**

No. Extra ports except those specified in Docker compose should not be open.

**Docker compose shows Postfix mail server, more information on how it works would be needed.**

Postfix mail server details/requirements: it runs as part of the docker compose, you just need to set environment variables to tell it which smtp relay host / user / password to use, see https://github.com/ssciwr/mondey/blob/main/DEPLOYMENT.md#emails

## Maintenance

**Are there deployment scripts or documentation available?**

Deployment scripts: in /. DEPLOYMENT.md covers deployment and setting the SSL keys and .env values. It also covers the email server and Deepl API (for translations).

As for documentation on development/entities in the code: The DEVELOPMENT.md file contains information about development. The generated OpenAPI files (types/services) and the Python model files (these use an ORM) are the best ways to understand the data models and how they can be interacted with, without diving head into complicated parts of the code. For statistics, the best approach is to read issues(including closed issues) about how that has changed.

**How are updates/patches currently handled?**

The CI builds production images when tests pass. The watchtower service will automatically update the site at 1AM each night (UTC). However it can also be manually updated by running docker compose pull and rebuilding (e.g. pruning cache).

As the Database data is mapped to volumes, this allows a new version without major downtime. When database migrations occur, a .sql file for that migration needs to be ran at the time of update. In that case, that .sql migration file will be included in a relevant commit for the update. So for any updates with SQL migration changes, it's best to handle that manually. (we have no plans for any updates like that at present).

**Is monitoring/logging already in place?**

Logs can be viewed on the VM with the command "docker compose logs"
Basic uptime monitoring here: https://ssciwr.github.io/monitoring/history/mondey
