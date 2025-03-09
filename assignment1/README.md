## The assignment1 of web service and cloud-based system


This project is a simple URL shortener service built using FastAPI. 
It allows users to shorten URLs, retrieve original URLs, update stored URLs, and delete URLs. The service also includes a comprehensive test suite using unittest.

### Installation 

#### Clone the repository
```
git clone https://github.com/calvinhaooo/web_service_assignment.git
```

#### Backend service
If you want to run the service, you should go to the directory first ```$ cd assignment1/```

Then, install the dependencies we set ```$ pip install -r requirements.txt```

Now, you can start our service by inputting ```$ python app.py ```

The service is running on ```http://127.0.0.1:8000```

#### Running the test

In the folder ```guide_unietest_and_tests```, there are some test units.

```
cd guide_unittest_and_tests
python test_1_marking_mk2.py
```

If you pass all the unit tests, you will see this below

```
Run 7 tests in 0.034s

OK
```

If you want to test our bonus points, you can run ```test_2.py```

``` python test_2.py ```

#### Structure
```
.
└── assignment1
    ├── README.md                    # The README of Assignment1
    ├── app.py                       # Entry of application
    └── guide_unittest_and_tests
        ├── read_from.csv            # The test case
        ├── test_1_marking_mk2.py    # The test units
        └── test_2.py                # our test for customized functions 
    └── services                     # Implementation of services
        ├── generate_id.py           # Generate Identifier
        ├── validate_url.py          # validate new url
        └── mode.py.                 # select LCG and BASE 
```



#### POSTMAN test for customized functions 

Test POST, GET and DELETE request
```
-----------------------------------------
POST http://127.0.0.1:8000/

# Below is the input json
{
  "value": "https://en.wikipedia.org/wii/Bitstream",
  "expiry_time": "2000",
  "user_id":"abc"
}
-----------------------------------------
GET http://127.0.0.1:8000/0?user_id=abc

DELETE http://127.0.0.1:8000/0?user_id=abc

GET http://127.0.0.1:8000/0?user_id=abc

```


Create 2 POST request by using different user id
```
-----------------------------------------
POST http://127.0.0.1:8000/
# the json of user "abc"
{
  "value": "https://en.wikipedia.org/wii/Bitstream",
  "expiry_time": "2000",
  "user_id":"abc"
}
-----------------------------------------
POST http://127.0.0.1:8000/
# the json of user guest
{
  "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
  "expiry_time": "2000",
}
-----------------------------------------
```


##### PUT --> test the update function
```
GET http://127.0.0.1:8000/0?user_id=abc

-----------------------------------------
PUT http://localhost:8000/0?user_id=abc

# the update json
{
    "url": "https://en.wikipedia.org/wiki/Caproni"
}

-----------------------------------------
GET http://127.0.0.1:8000/0?user_id=abc

##### GET ALL 
GET http://127.0.0.1:8000/

##### DELETE ALL 
DELETE http://127.0.0.1:8000/

GET http://127.0.0.1:8000/

```





##### test multi users

```
-----------------------------------------
POST http://127.0.0.1:8000/

{
  "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
  "expiry_time": "2000",
  "user_id":"abc"
}
-----------------------------------------
POST http://127.0.0.1:8000/

{
  "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
  "expiry_time": "2000",
}
-----------------------------------------
GET http://127.0.0.1:8000/0?user_id=abc

GET http://127.0.0.1:8000/0?user_id=guest

DELETE http://127.0.0.1:8000/0?user_id=abc

```


##### test recycle mechanism
```
POST http://127.0.0.1:8000/
-----------------------------------------
{
  "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
  "expiry_time": "2000",
  "user_id":"abc"
}

-----------------------------------------
POST http://127.0.0.1:8000/

{
  "value": "https://en.wikipedia.org/wiki/Torque_converter",
  "expiry_time": "2000",
  "user_id":"abc"
}
-----------------------------------------

DELETE http://127.0.0.1:8000/0?user_id=abc

# once it has been deleted, it will be put into the recycle pool
-----------------------------------------
POST http://127.0.0.1:8000/

{
  "value": "https://en.wikipedia.org/wiki/Network_topology",
  "expiry_time": "2000",
  "user_id":"abc"
}
-----------------------------------------
DELETE http://127.0.0.1:8000/
```


###### Expire
```
-----------------------------------------
POST http://127.0.0.1:8000/

{
  "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
  "expiry_time": "10",
  "user_id":"abc"
}
-----------------------------------------

# test beofore the link expries
GET http://127.0.0.1:8000/0?user_id=abc

# test after the link expires
GET http://127.0.0.1:8000/0?user_id=abc

```

Note: ----------------------------------------- is only for visualization.






