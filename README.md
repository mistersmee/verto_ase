# Verto ASE Challenge Submission

## Online Quiz Application API

I chose the backend project option: Online Quiz App API. I built the backend in Python, using `FastAPI` as the framework, with `SQLModel` for creating and interacting with the database (which is a simple local SQLite instance) and `Pydantic` for the data validation bits. The backend is served using `Uvicorn`.

The features I managed to build were:

- [X] Endpoint to create quizzes
- [X] Endpoint to add questions (Questions can be MCQs with single correct or multiple correct answers and text-based questions)
- [X] Endpoint to fetch all questions for a selected quiz. (The correct option isn't exposed as the correct option)
- [X] Endpoint to submit answers and get a score back, in the specified format.
- [X] Endpoint to get a list of all available quizzes (with a question count of that quiz as well).
- [X] Test cases for each of the above features.

## Instructions:
1. Clone the repo


			
		git clone git@github.com:mistersmee/verto_ase
		cd verto_ase
			
2. Create and activate the Python virtualenv


			
		python -m virtualenv venv
		source venv/bin/activate
			
3. Install the dependencies


   			
		pip install -r requirements.txt
			
4. Start the API

	
			
		uvicorn app:app --reload
			
5. Interact with the API using the tool of your choice (curl, Postman, etc.)

## Test cases

The project includes a test suite built using `PyTest`, so to run that, just input `pytest` in the project root directory.

## Assumptions & Design choices

Even though the challenge mentioned JavaScript/TypeScript was preferred, I went with Python, because it is the programming language I am most comfortable with. I am familiar with JavaScript, and I have begun to learn TypeScript, but Python is still the language I have the most familiarity with.

I chose FastAPI, because I wanted to use this challenge as an opportunity to try something new, most of the projects I've done have been either in Flask or Django, and I had heard good things about FastAPI, so I tried it here.
