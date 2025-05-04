# Flask Problem Details

## Overview
This module enhances Flask (or Flask OpenAPI) applications introducing structured error handling based on the [RFC 7807 Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807). It supports automatic validation error handling and provides detailed error responses, optionally including stack traces.

---

## Features
- **Problem Details Specification:** Conforms to the Problem Details for HTTP APIs standard.
- **Automatic Error Handling:** Registers handlers for common exceptions like validation errors and server-side issues.
- **Configurable Stack Traces:** Optionally include stack traces in error responses for easier debugging.
- **Flask support:** The package support Flask and/or Flask OpenAPI 3 applications.

---

## Installation
```bash
pip install flask-problem-details
```

---

## Usage

### 1. Configure the Application

```python
from flask_openapi3 import OpenAPI, Info
from werkzeug.exceptions import NotImplemented
from flask_problem_details import (
    configure_app, from_exception, ProblemDetails, ProblemDetailsError
)

# OpenAPI information
info: Info = Info(title="Flask OpenAPI 3 Example", version="1.0.0")
openapi_callback = lambda args : OpenAPI(__name__, info=info, **args)

app : OpenAPI = configure_app(app = openapi_callback, with_traceback=True)

@app.get("/authors")
def get_authors():
    raise NotImplemented()

@app.get("/books")
def get_books():
    description: str = "The method is not implemented"
    extras : dict = {"one": "extra value"}
    raise from_exception(NotImplementedError(description), extras = extras)

@app.get("/cats")
def get_cats():
   problem = ProblemDetails(status=412, title = "No shelter")
   raise ProblemDetailsError(problem)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
```

### 2. Error Response Example
When an error occurs, the module returns a JSON response similar to:
#### GET /authors
```json
{
  "status": 501,
  "title": "NotImplemented",
  "detail": "The server does not support the action requested by the browser.",
  "traceback": "Traceback (most recent call last):..."
}
```
#### GET /books
```json
{
  "status": 500,
  "title": "InternalServerError",
  "detail": "The method is not implemented",
  "traceback": "Traceback (most recent call last):...",
  "one": "extra value"
}
```
#### GET /cats
```json
{
  "status": 412,
  "title": "No shelter",
  "type": "uri:localhost:noshelter",
  "traceback": "Traceback (most recent call last):..."
}
```

---

## Core Components

### **Classes**
1. **`ProblemDetails`**: A Pydantic model representing the structure of an error response.
2. **`ProblemDetailsError`**: Exception class for handling problems.


### **Functions**
- `configure_app(app, with_traceback=False)`: Sets up the application with error handling.
- `activate_traceback() / deactivate_traceback()`: Enable or disable traceback inclusion.
- `from_exception(exception, extras)`: create a ProblemDetailsErrors from an exception.

---

## Extending the Module
To add custom error handling, register additional error handlers using Flask's `register_error_handler` method:
```python
@app.errorhandler(CustomException)
def handle_custom_exception(e):
    problem = ProblemDetails(status=412, title="Error", detail=str(e))
    return problem.to_http_response()
```

---

## License
This module is provided under the MIT License.

---

## Contributions
Contributions are welcome! Submit a pull request or open an issue on [GitHub](https://github.com/mikeymat/flask-problem-details).

---

## References
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask OpenAPI 3 Documentation](https://luolingchun.github.io/flask-openapi3/v4.x/Usage/Specification/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)