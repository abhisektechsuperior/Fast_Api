from sqlalchemy import Column, Integer,Date, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table for many-to-many relationship between Project and User
project_user_membership = Table(
    'project_user_membership',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

# Define the Project model
class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, index=True)
    project_detail = Column(String)
    


    # Relationship with User through the association table
       # Relationship with User
    users = relationship("User", back_populates="project")

# Define the User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))

    # Relationship with Project
    project = relationship("Project", back_populates="users")
# Define the Questions model
class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    choices = relationship('Choices', back_populates='question')

# Define the Choices model
class Choices(Base):
    __tablename__ = 'choices'
    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(String)
    is_correct = Column(Boolean)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = relationship('Questions', back_populates='choices')




class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    details = Column(String)

    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dob = Column(Date)  # New field for date of birth
    details = Column(String)  # New field for additional details
    department_id = Column(Integer, ForeignKey('departments.id'))

    department = relationship("Department", back_populates="employees")