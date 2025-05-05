import json
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse
from ..di import DIContainer
from ..routing import Registry
from ..enums import HTTPMethodType
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.routing import APIRoute, BaseRoute
from fastapi.middleware.cors import CORSMiddleware
import logging


class APIController:
    routes = []

    def __init__(self,
                 app: FastAPI,
                 cors_origins: List[str]=None,
                 generate_options_endpoints: bool=True,
                 generate_head_endpoints: bool=True,
                 debug_mode: bool=False
                 ) -> None:
        self.__app = app        
        self.__generate_options_endpoints = generate_options_endpoints
        self.__generate_head_endpoints = generate_head_endpoints   
        self.__debug_mode = debug_mode     
        if cors_origins is not None:
            self.__add_cors(cors_origins)

        self.__register_routes()

    def __register_routes(self) -> None:
        container = DIContainer(Registry())
        registry = container.get(Registry)
        self.__routes = registry.get_routes()

        for func, path, method, name, description in self.__routes:
            if hasattr(self,'_route_prefix'):
                path = self._route_prefix + path
                
            if hasattr(self, func.__name__) and callable(getattr(self, func.__name__)):
                bound_method = getattr(self, func.__name__) 
                if not self.__route_exists_for_method(path, method):           
                    self.__add_route(bound_method, method, path, name, description)

        if self.__generate_options_endpoints:
            self.__add_options_endpoints()

        self.__add_exception_handlers()

    def __add_route(self, bound_method: callable, method: HTTPMethodType, path: str, name: str = None, description: str = None) -> None:
        self.__app.add_api_route(
            path=path,
            endpoint=bound_method,
            methods=[method.value],
            name=name,
            description=description
        )
        if method.value == 'GET' and self.__generate_head_endpoints and not self.__route_exists_for_method(path, HTTPMethodType.HEAD):
            self.__app.add_api_route(
            path=path,
            endpoint=bound_method,
            methods=[HTTPMethodType.HEAD.value],
            name=f"{path}_head"
        )
    

    def __get_content(self, value):
        if isinstance(value, list): 
                return [self.__get_content(item) for item in value]                
        if isinstance(value, BaseModel):
            return value.model_dump_json()
        else:
            try:
                return json.dumps(value)
            except TypeError:
                return str(value)

    def __add_cors(self, cors_origins: List[str]) -> None:
        # noinspection PyTypeChecker
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def __add_options_endpoints(self) -> None:
        current_routes = self.__app.routes.copy()
        distinct_paths = set()
        for route in current_routes:
            if isinstance(route, APIRoute):
                distinct_paths.add(route.path)
        
        for path in distinct_paths:
            methods = self.__get_methods_for_path(path, current_routes)
            if not self.__route_exists_for_method(path, HTTPMethodType.OPTIONS):
                # noinspection PyTypeChecker
                self.__app.add_api_route(
                    path=path,
                    endpoint=self.create_options_endpoint(methods),
                    methods=[HTTPMethodType.OPTIONS.value],
                    name=f"{path}_options",
                    status_code=204,
                    response_class=Response,  
                    include_in_schema=True,  
                    responses={
                        204: {
                            "description": "No Content",  
                            "content": {},  
                            "headers": {
                                "Allow": {
                                    "description": "Allowed HTTP methods",
                                    "schema": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                )
                    

    def __route_exists_for_method(self, path: str, method_type: HTTPMethodType) -> bool:
        """
        Check if an OPTIONS route already exists for the specified path.
        """
        for route in self.__app.routes:
            if isinstance(route, APIRoute) and route.path == path and method_type.value in route.methods:
                return True
        return False   

    def __add_exception_handlers(self) -> None:
        self.__app.add_exception_handler(400, self.bad_request)
        self.__app.add_exception_handler(401, self.not_authorized)
        self.__app.add_exception_handler(403, self.forbidden)
        self.__app.add_exception_handler(404, self.not_found)
        self.__app.add_exception_handler(405, self.method_not_allowed)
        self.__app.add_exception_handler(422, self.unprocessable_entity)
        self.__app.add_exception_handler(500, self.internal_server_error)

    def bad_request(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(            
            exc, 
            400, 
            f"Bad Request for method {request.method} "
            f"and path {request.url.path}"
        )

    def not_authorized(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(            
            exc, 
            401, 
            f"Not authorized for method {request.method} "
            f"and path {request.url.path}"
        )

    def forbidden(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(            
            exc, 
            403, 
            f"Forbidden for method {request.method} "
            f"and path {request.url.path}"
        )

    def not_found(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(            
            exc, 
            404, 
            f"Path {request.url.path} not found"
        )

    def method_not_allowed(self, request: Request, exc: HTTPException) -> JSONResponse:        
        return self.__handle_exception(            
            exc, 
            405, 
            f"Method {request.method} not allowed for path {request.url.path}"
        )
    
    def unprocessable_entity(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(            
            exc, 
            422, 
            f"Unprocessable entity for method {request.method} "
            f"and path {request.url.path}"
        )

    def internal_server_error(self, request: Request, exc: HTTPException) -> JSONResponse:          
        return self.__handle_exception(            
            exc,
            500, 
            f"Internal server error for method {request.method} "
            f"and path {request.url.path}"
        )

    def __handle_exception(self, exc: HTTPException, status_code: int, error_message: str) -> JSONResponse:
        self.__log_exception(error_message, exc)
        content = {"detail": error_message}
        if hasattr(exc, "detail") and ((status_code == 500 and self.__debug_mode) or (status_code != 500)):
            content["errors"] = exc.detail
        
        return JSONResponse(status_code=status_code, content=content)

    def __log_exception(self, error_message: str, exc: HTTPException) -> None:
        if hasattr(exc, "detail"):
                error_message += f"; Exception: {exc.detail}"
        if logging.getLogger().hasHandlers():
            logger = logging.getLogger(__name__)            
            logger.error(error_message)
        else:
            print(error_message)
    
    @staticmethod
    def __get_methods_for_path(path: str, current_routes: List[BaseRoute]) -> List[str]:
        methods = set()
        for r in current_routes:
            if isinstance(r, APIRoute) and r.path == path:
                methods.update(r.methods)
        return list(methods)
    
    @staticmethod
    def create_options_endpoint(methods: list[str]):
        def options_endpoint():
            return Response(headers={"Allow": ", ".join(methods)}, status_code=204)
        return options_endpoint