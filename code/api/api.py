import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from code.brain import get_recommendation, get_historic_sample

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get('/predict')
def predict(year,week,investment,risk,industries):

    response = get_recommendation(year,week,investment,risk,industries)
    return response

@app.get('/historic')
def historic(year,week,investment,risk,industries):

    response = get_historic_sample(year,week,investment,risk,industries)
    return response
