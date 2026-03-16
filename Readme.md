# Flashcard Generator

Flashcard Generator is a web application that converts long learning content into small flashcards for easier memorization. Users can paste any length of text, and the system automatically divides the content into short learning chunks displayed as flashcards.

This project is built using Vue.js for the frontend, Django and Django REST Framework for the backend, and PostgreSQL for data storage.

---

## Features

* Paste large blocks of learning content
* Automatically split text into smaller flashcards
* Clean and simple flashcard interface
* Handles unlimited input text
* Backend API for flashcard generation
* Stores flashcards in PostgreSQL database
* RESTful architecture

---

## Tech Stack

Frontend

* Vue.js
* Axios
* CSS / Bootstrap or Tailwind

Backend

* Django
* Django REST Framework

Database

* PostgreSQL

---

## Project Structure

flashcard-generator

frontend

* Vue application
* Handles user input and displays flashcards

backend

* Django application
* API for generating flashcards
* Text processing logic
* Database management

---

## How It Works

1. User pastes a learning unit or notes into the input box.
2. The frontend sends the content to the backend API.
3. The backend processes the text and splits it into smaller meaningful sentences.
4. Each sentence becomes a flashcard.
5. Flashcards are returned to the frontend and displayed to the user.

---

## Backend Setup (Django)

Create virtual environment

python -m venv venv

Activate virtual environment

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Run migrations

python manage.py migrate

Start server

python manage.py runserver

Backend will run on

[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Frontend Setup (Vue)

Navigate to frontend folder

cd frontend

Install dependencies

npm install

Run development server

npm run serve

Frontend will run on

[http://localhost:8080](http://localhost:8080)

---

## API Endpoint

Generate Flashcards

POST /generate/

Request Body

{
"content": "Paste learning content here"
}

Response

[
"Flashcard sentence 1",
"Flashcard sentence 2",
"Flashcard sentence 3"
]

---

## Future Improvements

* Add AI-based flashcard generation
* Implement spaced repetition learning
* Add user authentication
* Save flashcard sets
* Export flashcards to PDF or Anki
* Add study mode with card flipping

---

## Use Case

This tool helps students quickly convert large study materials into smaller flashcards that are easier to memorize during exam preparation.

