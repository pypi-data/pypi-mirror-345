# Web API Controllers

## Description
Simple Web API controller framework for FastAPI

## Installation

To install this package, use pip:

```bash
pip install webapicontrollers
```

## Example
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from webapicontrollers import APIController, Get, Post, Patch, Delete, Put, RoutePrefix



@RoutePrefix('/test')
class TestController(APIController):

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app, cors_origins=['*'])    
    
    @Get('/', name='Optional name for OpenAPI docs', description='Optional description for OpenAPI docs')
    async def get(self) -> dict:
        return {"method": "GET", "path": "/"}  
    
    @Get('/400')
    async def get_bad_request(self) -> dict:
        raise HTTPException(status_code=400, detail="Bad Request")
    
    @Get('/401')
    async def get_not_authorized(self) -> dict:
        raise HTTPException(status_code=401, detail="Not Authorized")
    
    @Get('/403')
    async def get_forbidden(self) -> dict:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    @Get('/404')
    async def get_not_found(self) -> dict:
        raise HTTPException(status_code=404, detail="Not Found")
    
    @Get('/405')
    async def get_method_not_allowed(self) -> dict:
        raise HTTPException(status_code=405, detail="Method Not Allowed")
    
    @Get('/500')
    async def get_internal_server_error(self) -> dict:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    @Get('/{arg}')
    async def get_with_arg(self, arg) -> dict:
        return {"method": "GET", "path": "/", "arg": arg}

    @Post('/')
    async def post(self) -> dict:
        return {"method": "POST", "path": "/"}

    @Post('/{arg}')
    async def post_with_arg(self, arg) -> dict:
        return {"method": "POST", "path": "/", "arg": arg}
    
    @Put('/')
    async def put(self) -> dict:
        return {"method": "PUT", "path": "/"}
    
    @Put('/{arg}')
    async def put_with_arg(self, arg) -> dict:
        return {"method": "PUT", "path": "/", "arg": arg}
    
    @Patch('/')
    async def patch(self) -> dict:
        return {"method": "PATCH", "path": "/"}
    
    @Patch('/{arg}')
    async def patch_with_arg(self, arg) -> dict:
        return {"method": "PATCH", "path": "/", "arg": arg}
    
    @Delete('/')
    async def delete(self) -> dict:
        return {"method": "DELETE", "path": "/"}
    
    @Delete('/{arg}')
    async def delete_with_arg(self, arg) -> dict:
        return {"method": "DELETE", "path": "/", "arg": arg}
    
    def bad_request(self, request: Request, exc: HTTPException) -> JSONResponse:
        # Custom handling code
        return super().bad_request(request, exc)
    
    def not_authorized(self, request: Request, exc: HTTPException) -> JSONResponse:
        # Custom handling code
        return super().not_authorized(request, exc)
    
    def forbidden(self, request: Request, exc: HTTPException) -> JSONResponse:
        # Custom handling code
        return super().forbidden(request, exc)
    
    def not_found(self, request: Request, exc: HTTPException) -> JSONResponse:
        # Custom handling code
        return super().not_found(request, exc)
    
    def method_not_allowed(self, request: Request, exc: HTTPException) -> JSONResponse:
        # Custom handling code
        return super().method_not_allowed(request, exc)
    
    def internal_server_error(self, request: Request, exc: HTTPException) -> JSONResponse:
        # Custom handling code
        return super().internal_server_error(request, exc)


app = FastAPI()

TestController(app)
```

## Known Issues
If you overide the handler methods such as not_found etc. in more than one cotnroller only one handler will be registered on a last one wins basis.
Implementing a per route prefix handling system is on the to do list.

If you create a base controller class and then overide it's methods in a derived class the path needs to be the same in both methods. 
If you don't do this then FastAPI gets confused about which handler maps to which path.

## Caution
This project is in a very early state and might not be very useful to anyone yet. There is no support avilable, use at your own risk.

## License

This project is licensed under the [MIT License](LICENSE).
