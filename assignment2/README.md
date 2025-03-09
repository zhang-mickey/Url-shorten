## The assignment2 of web service and cloud-based system


This project is a simple URL shortener service built using FastAPI. 
It allows users to shorten URLs, retrieve original URLs, update stored URLs, and delete URLs. The service also includes a comprehensive test suite using unittest.

## How to run

for docker compose
```
cd assignment2
docker-compose build --no-cache 
docker-compose up
```

## Setup Nginx
```
nano /opt/homebrew/etc/nginx/nginx.conf
```
if using docker,use our nginx.conf
if not 
replace the server block with the following:
```
keepalive_timeout  65;

    #gzip  on;
    upstream authentication {
        server 127.0.0.1:5001;
    }

    upstream url_shorten {
        server 127.0.0.1:8000;
    }

    server {
        listen       8080;   
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;
    
        location /authentication/ {
            proxy_pass  http://authentication/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /url_shorten/ {
            proxy_pass  http://url_shorten/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    
        #error_page  404              /404.html;
        

```
test
``` 
curl -X POST http://localhost:8080/auth_service/users \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "123456"}'
    
    
curl -X POST http://localhost:8080/url_shorten_service/ \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "123456"}'
```

## Running the test

In the folder ```tests```, there are some test units.

```
cd tests
python test_app.py
```


for docker
set up auth_service
```
cd auth_service 
# create and run auth_service docker
docker build -t auth_service:v1 .
docker run -d --name auth_service_z --link db_services \
-e DATABASE_URL="postgresql://postgres:123456@db_services:5432/WSCBS_assignment" \
-p 5001:5001 auth_service:v1

#create and run auth_service database docker
docker run -d --name db_services -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=123456 -e POSTGRES_DB=WSCBS_assignment -p 5432:5432 postgres:15
#check
docker exec -it db_services psql -U postgres -d WSCBS_assignment
```
set up url_shorten_service 
```
cd url_shorten_service 
# create and run shorten_service docker
docker build -t url_shorten_service:v1 .
docker run -d --name url_shorten_service_z --link db_services \
-e DATABASE_URL="postgresql://postgres:123456@db_services:5432/WSCBS_assignment" \
-p 8000:8000 url_shorten_service:v1
#check
docker exec -it db_services psql -U postgres -d WSCBS_assignment
```
test
```
python test_app.py
```



 


## User authentication service
THis service is to handles user registration, login, and password management.
this service runs on port 5001.
If you want to run the service, you should go to the directory first ```$ cd assignment2/```

Then, install the dependencies we set ```$ pip install -r requirements.txt```

The service is running on ```http://127.0.0.1:8000```

## URL shorten service
this service runs on port 8000. 


## Databse

### Redis

```
brew services start redis
#check 
redis-cli ping
```

### PostgreSQL
The PostgreSQL database has its own container

```
postgres=# CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '123456';
CREATE ROLE
postgres=# ALTER ROLE postgres CREATEDB;
ALTER ROLE
```






### database for mac
    
```
brew install postgresql

brew services start postgresql

 CREATE USER assignment2 WITH SUPERUSER PASSWORD 'zhang69';
 CREATE DATABASE users OWNER assignment2;

without visualization
before run the code,prequisites(PostgreSQL,Redis,Nginx) will be needed.
```


```
install and run redis
install run postgresql
first run python url_db.py
then run python run_url.py
```


#### Structure
```
.
└── assignment2
    ├── README.md                    # The README of Assignment1
    ├── run_url.py                   # Entry of creating url
    ├── url_db.py                    # Create url database
    └── auth_service
        ├── tests                    # A test folder
        ├── auth_db.py.              # The database of auth
        ├── run_auth.py              # The entry of Authentication service
        └── Dockerfile
    └── url_shorten_service          # Implementation of services
        ├── services                 # The shorten url function
        └── tests                    # Generate Identifier
            └── test_app.py          # The test unit of assignment 
        ├── run_url.py               # The entry of shorten url service 
        ├── Dockerfile
        └── url_db.py.               # The database of URL
    └── db_services                  # The autiomatically deployment of database
        └── Dockerfile
```







