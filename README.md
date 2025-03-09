# web_service_assignment
This is the repo of Web service in UVA 2025 by Yinghao, Yifeng, Zheyuan.
There are several microservices:URL_shorten service,backend service,user authentication service,nginx
There are several main component that we use:postgresql,redis,nginx

The workflow diagram that illustrate how  users interact with the service as follows:



## URL shortening service

## User authentication
First,we encode the original URLs using hash function;
Second,check if they already exist in the database.

## database 


## GET
Returns a list of all stored short URL identifiers.

## POST

 URL to shorten 

Creates a new shortened URL and returns its id. If URL is invalid, returns 400.
## {id} GET

Redirects to the original URL corresponding to id. If not found, returns 404.

## {id} PUT
Updates the existing id mapping with a new URL.

## DETELE

## Redirect
redirect users to the original URL when they enter a shortened URL.

# Use Postman test the endpoints 
