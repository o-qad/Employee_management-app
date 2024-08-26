from datetime import date
from typing import List, Optional, Union
import pandas as pd
from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel, EmailStr, Field # type: ignore


def emp_csv():
    csv = pd.read_csv("Dummy_Employee_Data.csv")
    da = pd.DataFrame(csv)
    return da


def update_null_values(dff: pd.DataFrame, columns: list):
 
    for column in columns:
        dff[column] = dff[column].fillna('nul')
    return dff



class Employee:
    def __init__(self, employee_id: int, first_name: str, surname: str, email: EmailStr, department: str, position: str, salary: float, date_of_birth: str, start_date: str, end_date: Optional[str] = None):
        self.employee_id = employee_id
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.department = department
        self.position = position
        self.salary = salary
        self.date_of_birth = date_of_birth
        self.start_date = start_date
        self.end_date = end_date

class EmployeeCreate(BaseModel):
    First_Name: str = Field(min_length=1)
    Surname: str = Field(min_length=1)
    Email: EmailStr
    Department: str = Field(min_length=1)
    Position: str = Field(min_length=1)
    Salary: float = Field(gt=0)
    Date_of_Birth: str
    Start_date: Optional[str] = None
    End_date: Optional[str] = None
    class Config:
        json_schema = {
         'example': {
                'First_Name': 'John',
                'Surname': 'Doe',
                'Email': 'john.doe@example.com',
                'Department': 'Sales',
                'Position': 'Manager',
                'Salary': 60000.00,
                'Date_of_Birth': '1985-10-21',
                'Start_date': '2010-01-01',
                'End_date': '2024-05-20'
         }
        }

class EmployeeUpdate(BaseModel):
    Employee_ID: int
    First_Name: str = Field(min_length=1)
    Surname: str = Field(min_length=1)
    Email: EmailStr
    Department: str = Field(min_length=1)
    Position: str = Field(min_length=1)
    Salary: float = Field(gt=0)
    Date_of_Birth: str
    Start_date: Optional[str] = None
    End_date: Optional[str] = None

    class Config: 
        json_schema_extra = { 
            'example': {
                'Employee_ID': 1,
                'First_Name': 'John',
                'Surname': 'Doe',
                'Email': 'john.doe@example.com',
                'Department': 'Sales',
                'Position': 'Manager',
                'Salary': 60000.00,
                'Date_of_Birth': '1985-10-21',
                'Start_date': '2010-01-01',
                'End_date': '2024-05-20'
            }
        }

app = FastAPI()

@app.get("/")
def massage():
    return {"massage":"Welcome to Employee Management System."}

@app.get("/employees/get/all") 
def get_all_employees():   
    c = emp_csv()
    employees = c.to_dict(orient="records")
    return employees

@app.get("/employee/id/{employee_id}")
def get_employee(employee_id: int):
    df = emp_csv()
    employee = df[df["Employee_ID"] == employee_id]
    if employee.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee.iloc[0].to_dict()

@app.post("/employees/add")
def add_employee(employee: EmployeeUpdate):
    df = emp_csv()
    new_employee = pd.DataFrame([employee.dict(by_alias=True)])

    for column in new_employee.columns:
        if column not in df.columns:
            df[column] = None   

    new_employee = new_employee[df.columns]
    df = pd.concat([df, new_employee], ignore_index=True)
    df.to_csv("Dummy_Employee_Data.csv", index=False)
    
    columns_to_update = ['Start_date', 'End_date']
    dff = update_null_values(df, columns_to_update)
    dff.to_csv("Dummy_Employee_Data.csv", index=False)

    return {"message": "Employee added successfully", "id": df.index[-1]}


@app.put("/employees/update/{employee_id}")
def update_employee(employee_id: int, updated_employee: EmployeeCreate):
    df = emp_csv()
    index = df[df["Employee_ID"] == employee_id].index
    
    if index.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    updated_data = updated_employee.dict(exclude={"Employee_ID"})
     
    for key, value in updated_data.items():
        df.loc[index, key] = value

    df.to_csv("Dummy_Employee_Data.csv", index=False)
    return {"detail": "Employee updated successfully"}

@app.delete("/employees/delete/{employee_id}")  
def delete_employee(employee_id: int):
    df = emp_csv()
    index = df[df["Employee_ID"] == employee_id].index
    
    if index.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    df = df.drop(index)
    df.to_csv("Dummy_Employee_Data.csv", index=False)
    return {"message": "Employee deleted successfully"}

    




