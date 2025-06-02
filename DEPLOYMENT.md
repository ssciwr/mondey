# Deployment

Some information on how to deploy the website - currently it is deployed on a temporary heicloud VM.

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
0 0 * * 0 docker run -it --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d mondey.de
```

To check that the production website SSL certificates are configured correctly:

https://decoder.link/sslchecker/mondey.de/443

### Give users admin rights

To make an existing user with email `user@domain.com` into an admin, modify the users database, e.g.

```
sqlite3 db/users.db
sqlite> UPDATE user SET is_superuser = 1 WHERE email = 'user@domain.com';
sqlite> .quit
```
This only needs to be done for the first admin user in a new deployment, as they can then login and make other users admins from the admin interface.

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
