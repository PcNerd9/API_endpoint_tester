from typing import Annotated, List
from dataclasses import dataclass
from datetime import datetime
from endpoint_tester import EndpointTester

tester = EndpointTester()


def test1():
    @dataclass
    class User:
        email: Annotated[str, "strict"] = "ajayihabeeb@gmail.com"
        name: Annotated[str, "strict"] = "Habeeb Ajayi"
        stack: Annotated[str, "any"] = "python (FastAPI)"
        
    @dataclass
    class CatFactData:
        status: Annotated[str, "strict"] = "success"
        user: Annotated[User, "any"] = None
        timestamp: Annotated[float, "greater"] = 1759002313.994437
        fact: Annotated[str, "any"] = "According to a Gallup poll, most American pet owners obtain their cats by adopting strays."
        
        
        
    result = tester.test_runner(
        url="http://localhost:8000/me",
        method="get",
        expected_cls=CatFactData
    )
    print(result)
    if result["status"] == "pass":
        return True
    else: return False
    

def test2():
    token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4YzAwN2E1MzMwZWVmY2E0OThiNjBlNSIsImlhdCI6MTc1OTA2NTM5OSwiZXhwIjoxNzYxNjU3Mzk5fQ.Z7m_2Me-sFTZIdwSN_qfd5gj9e9VIILT7CEDjUG5jnM"
    url = "http://localhost:5000/api/v1/users/me"
    headers = {
        "Authorization": token
    }
    
    @dataclass
    class AgeRange:
        min: Annotated[int, "greater_equal"] = 18
        max: Annotated[int, "lesser_equal"] = 100
    
    @dataclass
    class Preference:
        ageRange: Annotated[AgeRange, "any"] = None
        distance: Annotated[int, "any"] = 50
        gender: Annotated[str, "strict"] = "female"
    
    @dataclass
    class User:
        _id: Annotated[str, "any"] = "68cf2b42e6aca9ef52f7f5f0"
        name: Annotated[str, "any"] =  "John Doe"
        email: Annotated[str, "strict"] = "john@example.com"
        gender: Annotated[str, "strict"] = "male"
        date_of_birth: Annotated[datetime, "strict d f(Y-M-D) utc"] =  "2025-04-20T00:00:00.000Z"
        bio: Annotated[str, "any"] = "I am human"
        address: Annotated[str, "any"] = "203, aaa London"
        religion: Annotated[str, "strict"] = "Christian"
        degree: Annotated[str, "any"] = "BSc"
        occupation: Annotated[str, "any"] = "Engineer"
        country: Annotated[str, "strict"] = "Nigeria"
        marital_status: Annotated[str, "strict"] = "Single"
        role: Annotated[str, "strict"] =  "user"
        status: Annotated[str, "strict"] = "active"
        created_at: Annotated[datetime, "any d f(Y-M-D:T) utc"] = "2025-09-20T22:31:30.699Z"
        # plan_id: Annotated[str, "any"] =  "68c0079e330eefca498b60ca"
        subscription_id: Annotated[str, "any"] = "68cf2b42e6aca9ef52f7f5f7"
        preferences: Preference = None
        
        
    result = tester.test_runner(
        url=url,
        expected_cls=User,
        method="get",
        headers=headers
    )
    print(result)
    if result["status"] == "pass":
        return True
    else: return False
    

def test3():
    token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4YzAwN2E1MzMwZWVmY2E0OThiNjBlNSIsImlhdCI6MTc1OTA2NTM5OSwiZXhwIjoxNzYxNjU3Mzk5fQ.Z7m_2Me-sFTZIdwSN_qfd5gj9e9VIILT7CEDjUG5jnM"
    url = "http://localhost:5000/api/v1/users/by-preferences"
    headers = {
        "Authorization": token
    }
    
    @dataclass
    class AgeRange:
        min: Annotated[int, "greater_equal"] = 18
        max: Annotated[int, "lesser_equal"] = 100
    
    @dataclass
    class Preference:
        ageRange: Annotated[AgeRange, "any"] = None
        distance: Annotated[int, "any"] = 50
        gender: Annotated[str, "strict"] = "female"
    
    @dataclass
    class User:
        _id: Annotated[str, "any"] = "68cf2b42e6aca9ef52f7f5f0"
        name: Annotated[str, "any"] =  "John Doe"
        email: Annotated[str, "any"] = "john@example.com"
        gender: Annotated[str, "strict"] = "female"
        date_of_birth: Annotated[datetime, "any d f(Y-M-D) utc"] =  "2025-04-20T00:00:00.000Z"
        bio: Annotated[str, "any"] = "I am human"
        address: Annotated[str, "any"] = "203, aaa London"
        religion: Annotated[str, "any"] = "Christian"
        degree: Annotated[str, "any"] = "BSc"
        occupation: Annotated[str, "any"] = "Engineer"
        country: Annotated[str, "strict"] = "nigeria"
        marital_status: Annotated[str, "strict"] = "single"
        role: Annotated[str, "strict"] =  "user"
        status: Annotated[str, "strict"] = "active"
        created_at: Annotated[datetime, "any d f(Y-M-D:T) utc"] = "2025-09-20T22:31:30.699Z"
        plan_id: Annotated[str, "any"] =  "68c0079e330eefca498b60ca"
        subscription_id: Annotated[str, "any"] = "68cf2b42e6aca9ef52f7f5f7"
        preferences: Preference = None
        
    
    @dataclass
    class ListUser:
        message: Annotated[str, "strict"] = "Retrieved User based on location only"
        users: Annotated[List[User], "strict len(8)"] = None
        

    result = tester.test_runner(
        url=url,
        expected_cls=ListUser,
        method="get",
        headers=headers
    )
    print(result)
    if result["status"] == "pass":
        return True
    else: return False
    



def main():
    score = 0
    test1_result = test1()
    if test1_result:
        score += 1
    
    test2_result = test2()
    if test2_result:
        score += 1
    
    test3_result = test3()
    if test3_result:
        score += 1
    print("Total score: ",score)
    
    
main()