# Website

current website url: http://54.202.105.156

## Description

This repository contains all the <b>back-end</b> source code of the UW Ocean Data Lab data visualization tool. All the front-end codes are already produced within the build file, so it's ready to be used.

If you want to see the detailed React code for the front-end interface, please go to https://github.com/AndrewLiu66/Ocean-lab-frontend

## Development

To download and run this repository, please follow the steps below in your terminal:

1. download the repository

```
$ git clone https://github.com/AndrewLiu66/Website-backend.git
```

2. go to the downloaded repository

```
$ cd Website-backend
```

3. creates and run a virtual environment

```
$ pip install virtualenv
$ virtualenv -p python3 venv
$ source ./venv/bin/activate
```

4. download all the dependencies

```
$ pip install -r requirements.txt
```

5. run the project

```
$ python3 app.py
```

6. open a browser and enter the following url

```
$ http://localhost:8000/
```

## Tech Stack

- Backend: Python Flask
- Frontend: React(the build file produced by https://github.com/AndrewLiu66/Ocean-web)
