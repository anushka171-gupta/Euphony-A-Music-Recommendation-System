# Euphony-A-Music-Recommendation-System
Microsoft Engage 2022 Project: Algorithms - Music Recommendation System


## Table of Contents
- [Introduction](#introduction)
- [Tech Stack Used](#tech-stack-used)
- [Recommendation System](#recommendation-system)
- [Setup](#setup)

## Introduction
Euphony is a website that offers thousands of songs to the users. From searching for a song to adding it to favourites list - Euphony allows a variety of features to help you find the music you are looking for. Get recommendations on the basis of your search result and your favourites list. Find similar artists to the ones you like.

## Tech Stack Used
- Django Framework
- Spotify API
- Rest Framework
- SQLite Database
- Python
- HTML
- CSS
- JavaScript

## Recommendation System
#### What recommendation technique was used in this project?
This project makes use of Content Based Filtering for suggesting the songs to the users based on the songs that are in their playlist or the search result. 
Content based filtering makes use of similarities in features of songs to suggest songs to the users. It has been implemented using K-means with cosine similarity. The dataset for the project was downloaded from kaggle.

#### Why was this technique used?
This algorithm was chosen as it does not require any data about the users which makes it easier to scale to a large number of users. The recommendations generated by content based filtering are tailored according to the user's interest. It avoids the "cold start" problem. Also it is generally easier to implement.

## Setup
The first thing to do is to clone the repository:
```
$ git clone https://github.com/anushka171-gupta/Euphony-A-Music-Recommendation-System
$ cd Euphony-A-Music-Recommendation-System-master
```
#### Activate virtual environment
```
$ env\Scripts\activate.bat
```
#### Installing requirements
```
(env)$ cd Algorithm
(env)$ pip install -r requirements.txt
```
#### Run the application
```
(env)$ python manage.py runserver
```
From the prompt copy the url: http://127.0.0.1:8000/

![prompt2](https://user-images.githubusercontent.com/79011361/170816322-c5e60e87-d2bc-4afd-9bb5-a851037ec744.png)


Paste the url in the browser followed by **Music/** as shown in the image below:

![Title](https://user-images.githubusercontent.com/79011361/170816902-2dc154e3-2aed-4bcb-b044-35a74c5cd5be.png)

The index page will open up:

![Screenshot (2070)](https://user-images.githubusercontent.com/79011361/170816984-b36c3475-5ec1-4197-9e79-ec0845213553.png)
