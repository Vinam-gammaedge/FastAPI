from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal
import json

app = FastAPI()

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data
def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)


class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of the patient',examples = ['P001'])]
    name:Annotated[str,Field(...,description='Name of the patient')]
    city:Annotated[str,Field(...,description='city of the patient')]
    age:Annotated[str,Field(...,description='Age of the patient')]
    gender:Annotated[Literal['male','female', 'others'],Field(...,description='gender of the  patient')]
    height:Annotated[float,Field(...,gt=0 , description='height of the patient in mtrs')]
    weight:Annotated[float,Field(...,gt=0 , description='weight of the patient in kgs')]
    @computed_field
    @property
    def  bmi(self) -> float:
        bmi  = round(self.weight/(self.height**2),2)
        return bmi
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi<18.5:
            return 'underweight'

        elif self.bmi < 30:
            return 'normal'


        else:
            return 'obese'


@app.get("/")
def hello():
    return {'message': 'Patient Management system API'}

@app.get("/about")
def about():
    return {'message': 'Fully functional API to manage your patient records'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID of the patient in the DB", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail='Patient not found')

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort by: height, weight, bmi"), order : str =  Query('asc',description='sort in asc or desc order') ):
    data = load_data()
    patients_list = list(data.values())  # Convert dict to list of patient objects

    if sort_by not in ["height", "weight", "bmi"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by field. Choose height, weight, or bmi.")
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400, details = f'invalid order select between asc and desc')

    sort_order  = True if  order  =='Desc' else False
    try:
        sorted_data = sorted(
            patients_list,
            key=lambda x: x[sort_by],
            reverse=sort_order

        )
        return sorted_data
    except KeyError:
        raise HTTPException(status_code=400, detail=f"{sort_by} field not present in some records.")


@app.post('/create')
def create_patient(patient:Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient already exists')

    data[patient.id]=patient.model_dump(exclude=['id'])

    save_data(data)
    return JSONResponse(status_code=201, content={"message": "patient created successfully"})









