from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health_check():
    """ Health check if the server is up """

    return {"message": "API is working"}
