from dataclasses import dataclass
from pydantic import EmailStr
from typing import Annotated

from endpoint_tester import EndpointTester

tester = EndpointTester()


def test1():
    @dataclass
    class User:
        email: Annotated[EmailStr, "any"] = "ajayihabeeb@gmail.com"
        name: Annotated[str, "any"] = "Habeeb Ajayi"
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
 