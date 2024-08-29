from fastapi import FastAPI , HTTPException , Depends
from pydantic import BaseModel
from typing import List , Annotated , Optional
import models
from database import engine, SessionLocal
from datetime import date
from sqlalchemy.orm import Session
#from schemas import DepartmentCreate, DepartmentResponse, EmployeeCreate, EmployeeResponse




app = FastAPI(title="Welcome to Our Fast API Project",
              description="Created By Abhisek")



# Create the tables
models.Base.metadata.create_all(bind=engine)



#for Choice Table
class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class ChoiceCreate(ChoiceBase):
    question_id: int

class ChoiceUpdate(ChoiceBase):
    pass

class ChoiceResponse(ChoiceBase):
    id: int
    question_id: int

    class Config:
        orm_mode = True

#For Question Table

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]
        
class QuestionResponse(BaseModel):
    id: int
    question_text: str
    choices: List[ChoiceBase]

    class Config:
        orm_mode = True

# Pydantic schemas for Project
class ProjectBase(BaseModel):
    project_name: str
    project_detail: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int

    class Config:
        orm_mode = True

# Pydantic schemas for User
class UserBase(BaseModel):
    user_name: str

class UserCreate(UserBase):
    project_id: int

class UserResponse(UserBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True

# Schema for adding a user to a project

class ProjectUserMembershipBase(BaseModel):
    project_id: int
    user_id: int




class EmployeeBase(BaseModel):
    name: str
    dob: Optional[date] = None
    details: Optional[str] = None
    department_id: int

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    

    class Config:
        orm_mode = True

class DepartmentBase(BaseModel):
    name: str
    details: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    employees: List[EmployeeResponse] = []

    class Config:
        orm_mode = True

        # Dependency for creating a session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Example of using the session
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/questions/{question_id}",tags=["Question"])
async def read_question(question_id: int, db: db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result

@app.post("/questions/",tags=["Question"])
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()
    return {"message": "Question created successfully"}

@app.put("/questions/{question_id}",tags=["Question"])
async def update_question(question_id: int, question: QuestionBase, db: db_dependency):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()

    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Update the question text
    db_question.question_text = question.question_text
    db.commit()

    # Update the choices
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=question_id)
        db.add(db_choice)
    db.commit()

    return {"message": "Question updated successfully"}

@app.delete("/questions/{question_id}",tags=["Question"])
async def delete_question(question_id: int, db: db_dependency):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Delete the question and its associated choices
    db.delete(db_question)
    db.commit()
    return {"message": "Question deleted successfully"}

# CRUD operations for Choice

# 1. Create a Choice (POST)
@app.post("/choices/", response_model=ChoiceResponse, tags=["Choices"])
async def create_choice(choice: ChoiceCreate, db: db_dependency):
    db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=choice.question_id)
    db.add(db_choice)
    db.commit()
    db.refresh(db_choice)
    return db_choice

# 2. Get a Choice by ID (GET)
@app.get("/choices/{choice_id}", response_model=ChoiceResponse, tags=["Choices"])
async def get_choice(choice_id: int, db: db_dependency):
    db_choice = db.query(models.Choices).filter(models.Choices.id == choice_id).first()
    if not db_choice:
        raise HTTPException(status_code=404, detail="Choice not found")
    return db_choice

# 3. Update a Choice by ID (PUT)
@app.put("/choices/{choice_id}", response_model=ChoiceResponse, tags=["Choices"])
async def update_choice(choice_id: int, choice: ChoiceUpdate, db: db_dependency):
    db_choice = db.query(models.Choices).filter(models.Choices.id == choice_id).first()
    if not db_choice:
        raise HTTPException(status_code=404, detail="Choice not found")

    db_choice.choice_text = choice.choice_text
    db_choice.is_correct = choice.is_correct
    db.commit()
    db.refresh(db_choice)
    return db_choice

# 4. Delete a Choice by ID (DELETE)
@app.delete("/choices/{choice_id}", tags=["Choices"])
async def delete_choice(choice_id: int, db: db_dependency):
    db_choice = db.query(models.Choices).filter(models.Choices.id == choice_id).first()
    if not db_choice:
        raise HTTPException(status_code=404, detail="Choice not found")

    db.delete(db_choice)
    db.commit()
    return {"message": "Choice deleted successfully"}



# CRUD operations for Project

# 1. Create a Project (POST)
@app.post("/projects/", response_model=ProjectResponse, tags=["Projects"])
async def create_project(project: ProjectCreate, db: db_dependency):
    db_project = models.Project(project_name=project.project_name, project_detail=project.project_detail)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# 2. Get a Project by ID (GET)
@app.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
async def get_project(project_id: int, db: db_dependency):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# 3. Update a Project by ID (PUT)
@app.put("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
async def update_project(project_id: int, project: ProjectUpdate, db: db_dependency):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.project_name = project.project_name
    db_project.project_detail = project.project_detail
    db.commit()
    db.refresh(db_project)
    return db_project

# 4. Delete a Project by ID (DELETE)
@app.delete("/projects/{project_id}", response_model=dict, tags=["Projects"])
async def delete_project(project_id: int, db: db_dependency):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

# CRUD operations for User

# 1. Create a User (POST)
@app.post("/users/", response_model=UserResponse, tags=["Users"])
async def create_user(user: UserCreate, db: db_dependency):
    db_user = models.User(user_name=user.user_name, project_id=user.project_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 2. Get Users by Project ID (GET)
@app.get("/users/{project_id}", response_model=List[UserResponse], tags=["Users"])
async def get_users_by_project(project_id: int, db: db_dependency):
    users = db.query(models.User).filter(models.User.project_id == project_id).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for this project")
    return users

# 3. Get a User by ID (GET)
@app.get("/users/id/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 4. Update a User by ID (PUT)
@app.put("/users/id/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(user_id: int, user: UserBase, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.user_name = user.user_name
    db.commit()
    db.refresh(db_user)
    return db_user

# 5. Delete a User by ID (DELETE)
@app.delete("/users/id/{user_id}", response_model=dict, tags=["Users"])
async def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.post("/projects/{project_id}/users/{user_id}", tags=["project_user_membership"])
async def add_user_to_project(project_id: int, user_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user is already a member of the project
    membership = db.execute(models.project_user_membership.select().where(
        models.project_user_membership.c.project_id == project_id,
        models.project_user_membership.c.user_id == user_id
    )).first()

    if membership:
        raise HTTPException(status_code=400, detail="User is already a member of this project")

    # Add the user to the project
    db.execute(models.project_user_membership.insert().values(project_id=project_id, user_id=user_id))
    db.commit()

    return {"message": "User added to project successfully"}

# Endpoint to list users in a project
@app.get("/projects/{project_id}/users", tags=["project_user_membership"])
async def list_users_in_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    users = db_project.users
    return users

# Endpoint to remove a user from a project
@app.delete("/projects/{project_id}/users/{user_id}", tags=["project_user_membership"])
async def remove_user_from_project(project_id: int, user_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Remove the user from the project
    db.execute(models.project_user_membership.delete().where(
        models.project_user_membership.c.project_id == project_id,
        models.project_user_membership.c.user_id == user_id
    ))
    db.commit()

    return {"message": "User removed from project successfully"}


# Create a Department
@app.post("/departments/", response_model=DepartmentResponse, tags=["Departments"])
async def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = models.Department(name=department.name, details=department.details)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

# Get a Department by ID
@app.get("/departments/{department_id}", response_model=DepartmentResponse, tags=["Departments"])
async def get_department(department_id: int, db: Session = Depends(get_db)):
    db_department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department

# Update a Department
@app.put("/departments/{department_id}", response_model=DepartmentResponse, tags=["Departments"])
async def update_department(department_id: int, department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db_department.name = department.name
    db_department.details = department.details
    db.commit()
    db.refresh(db_department)
    return db_department

# Delete a Department
@app.delete("/departments/{department_id}", response_model=dict, tags=["Departments"])
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    db_department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(db_department)
    db.commit()
    return {"message": "Department deleted successfully"}

# Create an Employee
@app.post("/employees/", response_model=EmployeeResponse, tags=["Employees"])
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = models.Employee(name=employee.name,
        details=employee.details,
        dob=employee.dob,
    
     department_id=employee.department_id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Get Employees by Department ID
@app.get("/employees/{department_id}", response_model=List[EmployeeResponse], tags=["Employees"])
async def get_employees_by_department(department_id: int, db: Session = Depends(get_db)):
    employees = db.query(models.Employee).filter(models.Employee.department_id == department_id).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for this department")
    return employees

# Update an Employee
@app.put("/employees/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
async def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db_employee.name = employee.name
    db_employee.department_id = employee.department_id
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Delete an Employee
@app.delete("/employees/{employee_id}", response_model=dict, tags=["Employees"])
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}

