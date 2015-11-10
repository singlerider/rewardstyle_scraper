# Rewardstyle Basic Scraper

Python 2.7.x

## Installation

Setting up a virtual environment (ideally), installing dependencies, and gaining
credentials.

Make sure to make a config file to place your credentials:

`cp config_example.py config.py`

### Virtual Environment

I would recommend running this in a virtual environment to keep your
dependencies in check. If you'd like to do that, run:

`sudo pip install virtualenv`

Followed by:

`virtualenv venv`

This will create an empty virtualenv in your project directory in a folder
called "venv." To enable it, run:

`source venv/bin/activate`

and your console window will be in that virtualenv state. To deactivate, run:

`deactivate`

### Dependencies

To install all dependencies locally (preferably inside your activated
virtualenv), run:

`pip install -r requirements.txt`

## To Run

Run

`./app.py`

or

`python app.py`

## To-do

Solve error message from DELETE request operation - it still goes through fine
