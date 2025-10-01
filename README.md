# Dynamic Endpoint Output Comparison

## 📌 Aim
The goal of this project is to **compare the output of an API endpoint with the expected output** in a **dynamic and flexible way**. This allows test cases to not only check for strict equality but also validate based on different conditions like type, range, or constraints.

---

## ⚙️ Plan

1. Use **`Annotated`** to specify the **type** of each field in the expected output along with **metadata** to define validation rules.
2. Define **comparison properties** that determine how actual values should be validated against expected values.
3. Implement a validation system that:
   - Calls the endpoint with the given `method` and `request_body`.
   - Handles failed responses gracefully by returning a structured JSON error.
   - Dynamically compares fields according to their annotations.
   - Supports iterables (lists, tuples) and applies validation per item.
   - Returns **pass/fail** results with detailed explanations when validation fails.

---

## 📑 Supported Metadata Properties

Each field in the output can have a **metadata property** that defines the comparison rule:

- `"strict"` → Value must be exactly equal.
- `"any"` → Value can be any valid instance of the annotated type.
- `"greater"` → For numbers, the value must be greater than the expected.
- `"lesser"` → For numbers, the value must be less than the expected.
- `"greater_equal"` → For numbers, value must be greater than or equal.
- `"lesser_equal"` → For numbers, value must be less than or equal.
- `"in"` -> expected value must be in the actual value

---

## 🔄 Flow (Pseudocode)

1. Call the API endpoint with:
   - **`method`** → HTTP method (GET, POST, etc.).
   - **`request_body`** → Request payload (if required).
2. If the endpoint **fails**, return:
   ```json
   {
     "status": "fail",
     "reason": "endpoint error",
     "response": { ... }  // actual response
   }
    ```

3. If the endpoint succeeds:
   - Compare output types with expected annotations.
   - If field type is iterable (list/tuple), loop through and validate each item.
   - If any comparison fails, return structured error with reason.

4. If all checks pass:
    ```json
    {
    "status": "pass"
    }
    ```

---  
##  📝 Example

**Endpoint**
```bash
    http://localhost:8000/api/v1/user/create
```

**Method**
```json
    "post"
```

**Request Body**
```json
{
  "email": "jonhdoe@example.com",
  "password": "john123",
  "username": "JohnDoe"
}
```

**Expected Output**
```python
from dataclasses import dataclass
from typing import Annotated
from datetime import datetime

@dataclass
class OutputData:
    email: Annotated[str, "strict"] = "johndoe@example.com"
    username: Annotated[str, "strict"] = "JohnDoe"
    id: Annotated[str, "any"]
    created_at: Annotated[datetime, "any"]
```
---

## 📅 Handling Datetime Fields
Datetime metadata can include **comparison rules** and **formatting instructions**:
Example:
```python
created_at: Annotated[datetime, "greater y f(Y-M-D:T) utc"]
```
### Rules for parsing metadata
1. Split metadata by space (`" "`).
2. If the list length > 1, continue parsing:
    - If string length = 1 → comparison level:
        - `y` = compare year only
        - `m` = compare year + month
        - `d` = compare year + month + day
        - `h` = compare year + month + day + hour
        - (continue down to seconds)
    - If string starts with `f(` → treat as format:
        - Example: `f(Y-M-D:T)` → custom datetime format.
    - Otherwise, assume it’s a timezone and handle with `try/except`.
3. After parsing rules, construct datetime and compare with actual value according to the first metadata token (greater, lesser, etc.).

---
## 📋 Handling Lists & Tuples
- If a field is a list or tuple:
    - Ensure the actual value is also a list or tuple.
    - Compare element types and validate each element recursively.
    - Example:
    ```python
    users: Annotated[List[User], "strict len(20)"]
    ```
    - `strict` → Elements must exactly match expected values.
    - `len(20)` → List must have exactly 20 elements.

---

## ✅ Summary
- **Flexible field comparison** using `Annotated`.
- **Supports multiple validation strategies** (`strict`, `any` , `greater`, etc.).
- **Datetime handling** with comparison granularity, formatting, and timezone.
- **Iterable validation** with element checks and length constraints.
- **Pass/Fail** reporting with structured explanations.

This approach makes API output validation **dynamic, reusable, and highly customizable**.