from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from dateutil import parser
import pytz 
import requests
from time import perf_counter
from typing import Annotated, Any, Dict, get_args, get_origin, Optional,  TypeVar

"""
Aim: compare the output of the endpoint output with the expected output, but want to make the comparison as dynamic as possible
plan:
1. use Annotated advantage to state the type of each field in the output and the a property as metadata
list of properties:
    i. "strict": it must strictly be equal
    ii. "any": the field can contain any value of the type specified
    iii. "greater": for integers or float, the value must be greater than the actual value
    iv. "lesser": for integers or float, the value must be lesser than the actual value
    v. "greater_equal": for integers or float, the value must be greater than or equal to the actual value
    vi. "lesser_equal": for integers or float, the value must be lesser than or equal to the actual value
psuedocode:
    i. call the endpoint with the method parameter and request_body parameter
    ii. if the endpoint fails return fail and the response it fail in a properly structured json
    iii. otherwise, compare if it type
    iv. if it is an iterator, loop through and compare each iterate
    v. if any of the iterate fail, return fail and why
    vi. return pass
    
example:
    endpoint: http://localhost:8000/api/v1/user/create
    method: "post"
    request_body: {
        "email": "jonhdoe@example.com",
        "password": "john123",
        "username: "JohnDoe"
    }
    expected_output: OutputData
    
    @dataclass
    class OutputData:
        email: Annotated[str, "strict"] = "johndoe@example.com"
        username: Annotated[str, "strict"] = "JohnDoe"
        id: Annotated[str, "any"]
        created_at: Annotated[datetime, "any"]
    
    handling date:
        created_at: Annotated[datetime, "greater y f(Y-M-D:T) utc"]
        1. split the metadata by space bar
        2. check the lenght of the list after spliting
        3. if greater than 1, continue with the below otherwise, just use the default format which what dateutils set, without timezone and compare to seconds
        4. loop through the remaining, 
            i.  check if the lenght of the string is 1 then that should be the level to compare it to (y = only compare the year, m = compare year and month, d = compare year, month and day, h = compare year, month, day and hour) and so on till you get to second
            ii. if the string start with f(, then replace f( and ) with "", the remaining is the format (which in our case Y-M-D:T) then format it using dateutils
            iii. and if its not any of the above, it should probably be the timezone, and we handle that with try and except statement
            iv. after constructing the datetime using the above rules, we can then compare it with the expected_datetime using the first list in our case (greater)
            
    handle list:
        check if the type is a list or tuple:
            check if the actual_value is a list of tuple too:
            users: Annotated[List[User], "strict len(20)"] flexible or strict (lenght)
    
"""

T = TypeVar("T")

class EndpointTester:
    
    def compare_value(self, expected_type, rule, expected_value, actual_value):
        
        if not isinstance(actual_value, expected_type):
            return False, f"Type mismatch: expected {expected_type}, got {type(actual_value)}"
        
        if rule == "strict":
            if actual_value != expected_value:
                return False, f"Strict mismatch: expected {expected_value}, got {actual_value}"
        
        elif rule == "any":
            return True, None
        
        elif rule == "in":
            if expected_value not in actual_value:
                return False, f"Expected {expected_value} present in {actual_value}"
        
        elif rule == "greater":
            if not actual_value > expected_value:
                return False, f"Expected greater than {expected_value}, got {actual_value}"
            
        elif rule == "lesser":
            if not actual_value < expected_value:
                return False, f"Expected lesser than {expected_value}, got {actual_value}"
        
        elif rule == "greater_equal":
            if not actual_value >= expected_value:
                return False, f"Expected greater than or equat to {expected_value}, got {actual_value}"
        
        elif rule == "lesser_than":
            if not actual_value <= expected_value:
                return False, f"Expected lesser than or equal to {expected_value}, got {actual_value}"
        
        return True, None
    

    def date_parser(self, date_str: str, rules: list[str]) -> datetime | None:
        try:
            
            dt = parser.parse(date_str)

            levels = {
                "y": "%Y",
                "m": "%Y-%m",
                "d": "%Y-%m-%d",
                "h": "%Y-%m-%d %H",
                "min": "%Y-%m-%d %H:%M",
                "s": "%Y-%m-%d %H:%M:%S",
            }

            for rule in rules:
                rule = rule.strip().lower()

                if rule in levels:
                    fmt = levels[rule]
                    dt = datetime.strptime(dt.strftime(fmt), fmt)
                    

                elif rule.startswith("f(") and rule.endswith(")"):
                    fmt = rule[2:-1]
                    fmt = (
                        fmt.replace("y", "%Y")
                           .replace("m", "%m")
                           .replace("d", "%d")
                           .replace("t", "%H:%M:%S")
                    )
                    dt = datetime.strptime(dt.strftime(fmt), fmt)
                else:
                    try:
                        tz = pytz.timezone(rule)
                        if dt.tzinfo is None:
                            dt = tz.localize(dt)
                        else:
                            dt = dt.astimezone(tz)
                    except pytz.UnknownTimeZoneError:
                        raise ValueError(f"Unknown timezone: {rule}")

            return dt

        except Exception as e:
            print("Error occurred while parsing datetime:", str(e))
            return None

    
    def validate_response(self, expected_cls, response_data: dict):
        for f in fields(expected_cls):
            expected_type = f.type
            
            if f.name == "status_code":
                continue

            if get_origin(expected_type) is Annotated:
                type_, rule = get_args(expected_type)
            else:
                type_, rule = expected_type, "strict"

            actual_value = response_data.get(f.name, "missing")
            if actual_value == "missing":
                return {"status": "fail", "field": f.name, "reason": "field is missing in the actual response"}
            

            if get_origin(type_) is list or get_origin(type_) is tuple:
                if not isinstance(actual_value, (list, tuple)):
                    return {"status": "fail", "field": f.name, "rL[Useason": f"Expected {type_}, got {type(actual_value)}"}
                
                if rule.startswith("strict"):
                    length_value = rule.split(" ")[1]
                    if not length_value.startswith("len(") or not length_value.endswith(")"):
                        return {"status": "fail", "field": f.name, "reason": f"invalid length declaration, expected len(value) got {length_value}"}
                    lenght = int(length_value[4:-1])
                    
                    if len(actual_value) != lenght:
                        return {"status": "fail", "field": f.name, "reason": f"Length mismatch, expected lenght {lenght} got {len(actual_value)}"}

                type_ = get_args(type_)[0]
                for value in actual_value:
                    result = self.validate_response(type_, value)
                    if result["status"] == "fail":
                        return result
                
                continue
            
            if is_dataclass(type_):
                result = self.validate_response(type_, actual_value)
                if result["status"] == "fail":
                    return result
                else:
                    continue
            
            expected_value = getattr(expected_cls, f.name)
            
            if type_ is datetime:
                actual_value = self.date_parser(actual_value, rule.split()[1:])
                if actual_value is None:
                    return {"status": "fail", "field": f.name, "reason": "field not a valid datetime"}
                if isinstance(expected_value, str):
                    expected_value = self.date_parser(expected_value, rule.split()[1:])
                    if expected_value is None:
                        return {"status": "fail", "field": f.name, "reason": "expected datetime value is not in a valid format"}
                
            ok, reason = self.compare_value(type_, rule.split()[0], expected_value, actual_value)
            
            if not ok:
                return {"status": "fail", "field": f.name, "reason": reason}
        
        return {"status": "pass"}
    
        
    
    def test_runner(
        self,
        url: str,
        method: str,
        expected_cls: type[T], 
        request_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] =  None
        
    ) -> Dict[str, Any]:
        
        try:
            if method.lower() == "post":
                r = requests.post(url, json=request_body, headers=headers)
            elif method.lower() == "get":
                r = requests.get(url, params=request_body, headers=headers)
            elif method.lower() == "put":
                r = requests.put(url, json=request_body, headers=headers)
            else:
                return {"status": "fail", "reason": f"Unsupported method: {method}"}
            
            status_code = None
            if hasattr(expected_cls, "status_code"):
                status_code = getattr(expected_cls, "status_code")
            
            if status_code:
                if r.status_code != status_code:
                    return {"status": "fail", "reason": f"Expected status code {status_code}, got {r.status_code}"} 
            else:      
                if r.status_code != 200:
                    return {"status": "fail", "reason": f"HTTP {r.status_code}", "response": r.text}
                
            response_data = r.json()
            return self.validate_response(expected_cls, response_data)
        
        except Exception as e:
            return {"status": "fail", "reason": str(e)}
            
            
    def test_caching(
        self,
        url: str,
        method: str,
        expected_cls: type[T],
        request_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        expected_speedup: Optional[int] = 10
    ) -> Dict[str, Any]:
        
        each_req_time_elapse = []
        for _ in range(2):
            start = perf_counter()
            
            result = self.test_runner(url, method, expected_cls, request_body, headers)
            
            end = perf_counter()
            each_req_time_elapse.append(end - start)
        
        speedup = each_req_time_elapse[0] // each_req_time_elapse[1]

        if speedup < expected_speedup:
            return {"status": "fail", "reason": f"Expected speedup is {expected_speedup}, got {speedup}"}
        
        return {"status": "pass"}

            
        


