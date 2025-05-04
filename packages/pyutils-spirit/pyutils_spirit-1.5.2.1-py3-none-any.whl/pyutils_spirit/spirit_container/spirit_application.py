# @Coding: UTF-8
# @Time: 2024/9/22 17:15
# @Author: xieyang_ls
# @Filename: spirit_application.py
import os

import json

import inspect

import importlib.util

from threading import Lock

from typing import Callable

from cgi import FieldStorage

from types import FunctionType, MethodType

from pyutils_spirit.util.set import Set, HashSet

from pyutils_spirit.util.json_util import deep_dumps

from logging import info, INFO, basicConfig, exception

from http.server import BaseHTTPRequestHandler, HTTPServer

from pyutils_spirit.style.resources import draw_spirit_banner

from pyutils_spirit.util.assemble import Assemble, HashAssemble

from pyutils_spirit.spirit_container.request_result import Result

from pyutils_spirit.concurrent_thread.thread_holder import ThreadHolder

from pyutils_spirit.spirit_container.multipart_file import MultipartFile

from pyutils_spirit.concurrent_thread.thread_executor import ThreadExecutor

from pyutils_spirit.exception.exception import BusinessException, SpiritContainerServiceException

basicConfig(level=INFO)

SIGNATURE_SET: set[str] = {"Component", "Mapper", "Service", "Controller",
                           "WebSocketServerEndPoint", "RequestInterceptor", "ExceptionAdvice"}


class SpiritApplication:
    start_status: bool = None

    __request_body_key__: str = None

    __unified_response_type__: bool = None

    __current_file__: str = None

    __container: ThreadHolder[str, object] = None

    __auto_wired_set__: set[object] = None

    __lock: Lock = None

    __executor: ThreadExecutor = None

    __controller_paths_set: set[str] = None

    __exception_advice_methods__: Assemble[type, MethodType] = None

    __interceptor_paths_set: set[str] = None

    __interceptor_function_before__: Callable[[BaseHTTPRequestHandler], tuple[int, bool]] = None

    __interceptor_function_after__: Callable[[BaseHTTPRequestHandler], None] = None

    def __init__(self, __file__):
        SpiritApplication.__lock = Lock()
        self.__executor = ThreadExecutor()
        self.__current_file__ = os.path.basename(__file__)
        SpiritApplication.__container = ThreadHolder.constructor()
        self.__auto_wired_set__ = set()
        SpiritApplication.__controller_paths_set = set()
        SpiritApplication.__exception_advice_methods__ = HashAssemble()
        SpiritApplication.__interceptor_paths_set = set()

    def start_service(self, host: str, port: int,
                      unified_response_type: bool = True,
                      request_body_key: str = "body"):
        SpiritApplication.__lock.acquire()
        try:
            if SpiritApplication.start_status is True:
                raise SpiritContainerServiceException
            SpiritApplication.start_status = True
        finally:
            SpiritApplication.__lock.release()
        SpiritApplication.__unified_response_type__ = unified_response_type
        SpiritApplication.__request_body_key__ = request_body_key
        draw_spirit_banner()
        self.__scan_modules(os.getcwd())
        self.__start_service(host=host, port=port)

    def __scan_modules(self, work_directory: str):
        for dirpath, dir_names, filenames in os.walk(work_directory):

            for file_name in filenames:
                if file_name == "__init__.py":
                    continue
                if file_name.endswith('.py'):
                    file_path = os.path.join(dirpath, file_name)
                    self.__load_module(file_path)
        self.__auto_injected()

    def __load_module(self, file_path):
        current_file_path = os.path.abspath(self.__current_file__)
        if file_path == current_file_path:
            return None
        module_path = file_path[:-3]
        module_name = os.path.basename(module_path)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.__analyze_module(module)

    def __analyze_module(self, module) -> None:
        unique_modules: Set[object] = HashSet()
        for name, obj in inspect.getmembers(module):
            if obj is None:
                continue
            if obj not in unique_modules:
                unique_modules.add(obj)
                if isinstance(obj, FunctionType | type):
                    decorator = getattr(obj, "__decorator__", None)
                    if decorator in SIGNATURE_SET:
                        instance = obj()
                        self.__auto_wired_set__.add(instance)
                        if decorator == "Controller":
                            params = getattr(obj, "__decorator_params__")
                            SpiritApplication.__controller_paths_set.add(params)
                        elif decorator == "ExceptionAdvice":
                            for method_name, method in inspect.getmembers(instance):
                                if isinstance(method, MethodType):
                                    decorator = getattr(method, "__decorator__", None)
                                    if decorator == "ThrowsException":
                                        params = getattr(method, "__decorator_params__")
                                        SpiritApplication.__exception_advice_methods__.put(params, method)
                        elif decorator == "RequestInterceptor":
                            SpiritApplication.__interceptor_paths_set = getattr(obj, "__decorator_params__")
                            for method_name, method in inspect.getmembers(instance):
                                if isinstance(method, MethodType):
                                    decorator = getattr(method, "__decorator__", None)
                                    if decorator == "InterceptorBefore":
                                        SpiritApplication.__interceptor_function_before__ = method
                                    elif decorator == "InterceptorAfter":
                                        SpiritApplication.__interceptor_function_after__ = method

    def __auto_injected(self) -> None:
        for instance in self.__auto_wired_set__:
            for method_name, method in inspect.getmembers(instance):
                if isinstance(method, MethodType):
                    decorator = getattr(method, "__decorator__", None)
                    if decorator == "Resource":
                        if hasattr(method, "__self__") and isinstance(method.__self__, type):
                            method(cls=type(instance), resources={})
                        else:
                            method(self=instance, resources={})

    def __start_service(self, host: str, port: int):
        server_address: tuple[str, int] = (host, port)
        service = HTTPServer(server_address, self.RequestHandler)
        info("Spirit Container Service Startup successfully")
        info(f"Listening on Server: {host}:{port}")
        self.__executor.execute(service.serve_forever)

    @classmethod
    def __do_interceptor_function__(cls, request_path: str) -> bool:
        if len(cls.__interceptor_paths_set) == 0:
            return False
        for path in cls.__interceptor_paths_set:
            path_list = request_path.split(path, maxsplit=1)
            if len(path_list) == 1:
                return False
            if path_list[0] == "" and path_list[1][0] == "?":
                return True
        return False

    @classmethod
    def __get_func_kwargs__(cls, path: str, method_type: str) -> [object, callable, dict]:
        cls.__lock.acquire()
        try:
            for controller_path in cls.__controller_paths_set:
                path_list = path.split(controller_path, maxsplit=1)
                if len(path_list) == 1:
                    continue
                if path_list[0] != "":
                    continue
                controller_func_path = path_list[1]
                if len(path_list) == 2 and controller_func_path[0] == "/":
                    controller = cls.__container.get_holder(key=controller_path)
                    for method_name, method in inspect.getmembers(controller):
                        decorator = getattr(method, "__decorator__", None)
                        if decorator is method_type:
                            func_path = getattr(method, "__decorator_path__")
                            func_path_list = controller_func_path.split(func_path, maxsplit=1)
                            if len(func_path_list) == 1:
                                continue
                            func_args = func_path_list[1]
                            if len(func_path_list) > 1:
                                if func_args == "":
                                    return method, None
                                elif func_args[0] == "?":
                                    kwargs = dict()
                                    for param in func_args.split("?")[1].split("&"):
                                        if "=" in param:
                                            key = param.split("=")[0].strip()
                                            value = param.split("=")[1].strip()
                                            kwargs[key] = value
                                    return method, kwargs
        finally:
            cls.__lock.release()
        raise ValueError(f"please check the path {path} of {method_type} Method")

    class RequestHandler(BaseHTTPRequestHandler):

        __data__ = None

        __response__ = None

        __is_interceptor__: bool = False

        __is_pass__: bool = False

        __response_code__: int = 200

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __request_exception_advice__(self, e: Exception):
            exception(e)
            self.__response_code__ = 500
            self.__response__ = str(e)
            method = SpiritApplication.__exception_advice_methods__.get(key=type(e))
            if method is not None:
                self.__response__ = method(e)
            elif SpiritApplication.__unified_response_type__ is True:
                if isinstance(e, BusinessException):
                    self.__response__ = Result.WARN(self.__response__)
                else:
                    self.__response__ = Result.ERROR(self.__response__)

        def __is_interceptor_func__(self):
            self.__is_interceptor__ = SpiritApplication.__do_interceptor_function__(self.path)
            if self.__is_interceptor__:
                if SpiritApplication.__interceptor_function_before__ is not None:
                    self.__response_code__, self.__is_pass__ = SpiritApplication.__interceptor_function_before__(self)
                    if self.__is_pass__ is False:
                        self.__response__ = Result.WARN(f"the request '{self.path}' is be intercepted")
                        return True
            return False

        def __request_end_func__(self):
            self.send_response(self.__response_code__)
            intercepted = self.headers["X-Intercepted"]
            if intercepted == "True":
                self.send_header(keyword="X-Intercepted", value="True")
            else:
                self.send_header(keyword="X-Intercepted", value="False")
            self.send_header(keyword='Access-Control-Allow-Origin', value='*')
            self.send_header(keyword='Content-type', value='application/json')
            self.end_headers()
            self.wfile.write(deep_dumps(data=self.__response__).encode('utf-8'))
            if self.__is_interceptor__ and self.__is_pass__:
                if SpiritApplication.__interceptor_function_after__ is not None:
                    SpiritApplication.__interceptor_function_after__(self)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

        def do_GET(self):
            try:
                if self.__is_interceptor_func__():
                    return None
                func, kwargs = SpiritApplication.__get_func_kwargs__(self.path, "GET")
                if kwargs is not None:
                    self.__response__ = func(**kwargs)
                else:
                    self.__response__ = func()
                if SpiritApplication.__unified_response_type__ is True:
                    self.__response__ = Result.SUCCESS(self.__response__)
            except Exception as e:
                self.__request_exception_advice__(e)
            finally:
                self.__request_end_func__()

        def __get_post_file__(self, post_body_length) -> (dict, bool):
            if self.headers['Content-Type'].startswith('multipart/form-data'):
                # 解析请求体
                field_storage = FieldStorage(fp=self.rfile,
                                             headers=self.headers,
                                             environ={'REQUEST_METHOD': 'POST'})
                form_data: dict = {}
                for form in field_storage.list:
                    if form.name in form_data:
                        data = form_data[form.name]
                        if not isinstance(data, list):
                            form_data[form.name] = [data]
                        if form.filename is not None and isinstance(form.value, bytes):
                            form_data[form.name].append(MultipartFile(filename=form.filename,
                                                                      file_bytes=form.value))
                        else:
                            form_data[form.name].append(form.value)
                    else:
                        if form.filename is not None and isinstance(form.value, bytes):
                            form_data[form.name] = MultipartFile(filename=form.filename,
                                                                 file_bytes=form.value)
                        else:
                            form_data[form.name] = form.value
                return form_data
            else:
                data = self.rfile.read(post_body_length)
                return {
                    SpiritApplication.__request_body_key__: json.loads(data)
                }

        def do_POST(self):
            post_body_length = int(self.headers['Content-Length'])
            try:
                if self.__is_interceptor_func__():
                    return None
                func, kwargs = SpiritApplication.__get_func_kwargs__(self.path, "POST")
                if post_body_length > 0:
                    self.__data__ = self.__get_post_file__(post_body_length)
                else:
                    self.__response_code__ = 400
                    raise ValueError("Post Method: Request Body must be not empty.")
                if kwargs is not None:
                    self.__response__ = func(**kwargs, **self.__data__)
                else:
                    self.__response__ = func(**self.__data__)
                if SpiritApplication.__unified_response_type__ is True:
                    self.__response__ = Result.SUCCESS(self.__response__)
            except Exception as e:
                self.__request_exception_advice__(e)
            finally:
                self.__request_end_func__()

        def __set_request_arguments(self, kwargs, func):
            if kwargs is not None:
                if self.__data__ is None:
                    self.__response__ = func(**kwargs)
                else:
                    self.__response__ = func(**kwargs, **self.__data__)
            else:
                if self.__data__ is None:
                    self.__response__ = func()
                else:
                    self.__response__ = func(**self.__data__)

        def do_PUT(self):
            put_body_length = int(self.headers['Content-Length'])
            if put_body_length > 0:
                data = self.rfile.read(put_body_length)
                self.__data__ = {
                    SpiritApplication.__request_body_key__: json.loads(data)
                }
            else:
                self.__data__ = None
            try:
                if self.__is_interceptor_func__():
                    return None
                func, kwargs = SpiritApplication.__get_func_kwargs__(self.path, "PUT")
                self.__set_request_arguments(kwargs=kwargs, func=func)
                if SpiritApplication.__unified_response_type__ is True:
                    self.__response__ = Result.SUCCESS(self.__response__)
            except Exception as e:
                self.__request_exception_advice__(e)
            finally:
                self.__request_end_func__()

        def do_DELETE(self):
            content = self.headers['Content-Length']
            if content is not None:
                delete_body_length = int(content)
                if delete_body_length > 0:
                    data = self.rfile.read(delete_body_length)
                    self.__data__ = {
                        SpiritApplication.__request_body_key__: json.loads(data)
                    }
                else:
                    self.__data__ = None
            else:
                self.__data__ = None
            try:
                if self.__is_interceptor_func__():
                    return None
                func, kwargs = SpiritApplication.__get_func_kwargs__(self.path, "DELETE")
                self.__set_request_arguments(kwargs=kwargs, func=func)
                if SpiritApplication.__unified_response_type__ is True:
                    self.__response__ = Result.SUCCESS(self.__response__)
            except Exception as e:
                self.__request_exception_advice__(e)
            finally:
                self.__request_end_func__()
