# @Coding: UTF-8
# @Time: 2024/9/24 12:58
# @Author: xieyang_ls
# @Filename: annotation.py

from argparse import ArgumentTypeError

from http.server import BaseHTTPRequestHandler

from pyutils_spirit.exception.exception import NoneSignatureError

from pyutils_spirit.concurrent_thread.thread_holder import ThreadHolder


class ContainerAnnotation:
    __spirit_application_container: ThreadHolder[str, object] = ThreadHolder.constructor()

    @classmethod
    def component(cls, signature: str) -> callable:
        if not isinstance(signature, str):
            raise NoneSignatureError
        if len(signature) == 0:
            raise ValueError("Component: Signature cannot be empty")

        def get_component_cls(other_cls):

            def get_component_instance(*args, **kwargs) -> object:
                instance = cls.__spirit_application_container.get_holder(key=signature)
                if instance is None:
                    instance = other_cls(*args, **kwargs)
                    cls.__spirit_application_container.set_holder(key=signature, value=instance)
                return instance

            get_component_instance.__decorator__ = "Component"
            get_component_instance.__decorator_params__ = signature
            return get_component_instance

        return get_component_cls

    @classmethod
    def mapper(cls, signature: str) -> callable:
        if not isinstance(signature, str):
            raise NoneSignatureError
        if len(signature) == 0:
            raise ValueError("Mapper: Signature cannot be empty")

        def get_mapper_cls(other_cls):

            def get_mapper_instance(*args, **kwargs) -> object:
                instance = cls.__spirit_application_container.get_holder(key=signature)
                if instance is None:
                    instance = other_cls(*args, **kwargs)
                    cls.__spirit_application_container.set_holder(key=signature, value=instance)
                return instance

            get_mapper_instance.__decorator__ = "Mapper"
            get_mapper_instance.__decorator_params__ = signature
            return get_mapper_instance

        return get_mapper_cls

    @classmethod
    def service(cls, signature: str) -> callable:
        if not isinstance(signature, str):
            raise NoneSignatureError
        if len(signature) == 0:
            raise ValueError("Service: Signature cannot be empty")

        def get_service_cls(other_cls):

            def get_service_instance(*args, **kwargs) -> object:
                instance = cls.__spirit_application_container.get_holder(key=signature)
                if instance is None:
                    instance = other_cls(*args, **kwargs)
                    cls.__spirit_application_container.set_holder(key=signature, value=instance)
                return instance

            get_service_instance.__decorator__ = "Service"
            get_service_instance.__decorator_params__ = signature
            return get_service_instance

        return get_service_cls

    @classmethod
    def controller(cls, path: str) -> callable:
        if not isinstance(path, str):
            raise NoneSignatureError
        if len(path) == 0:
            raise ValueError("Controller: path cannot be empty")

        def get_controller_cls(other_cls):

            def get_controller_instance(*args, **kwargs) -> object:
                instance = cls.__spirit_application_container.get_holder(key=path)
                if instance is None:
                    instance = other_cls(*args, **kwargs)
                    cls.__spirit_application_container.set_holder(key=path, value=instance)
                return instance

            get_controller_instance.__decorator__ = "Controller"
            get_controller_instance.__decorator_params__ = path
            return get_controller_instance

        return get_controller_cls

    @classmethod
    def resource(cls, names: list[str] | str) -> callable:
        if not isinstance(names, list | str):
            raise ValueError("Resource: the signature of type must be list or str")
        if not all(isinstance(name, str) for name in names):
            raise ValueError("All elements in the list must be strings")
        if len(names) == 0:
            raise ValueError("the names must not be empty")

        def decorator_func(func):
            def wrapper(*args, **kwargs):
                if isinstance(names, str):
                    resources = cls.__spirit_application_container.get_holder(key=names)
                    if resources is None:
                        raise ValueError(f"the signature {names} does not exist")
                else:
                    resources = kwargs["resources"]
                    for name in names:
                        instance = cls.__spirit_application_container.get_holder(key=name)
                        if instance is None:
                            raise ValueError(f"the signature {name} does not exist")
                        resources[name] = instance
                func(args[0], resources)

            wrapper.__decorator__ = "Resource"
            return wrapper

        return decorator_func

    @classmethod
    def get(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('GET Method: path should be a string')
        if len(path) == 0:
            raise ValueError('GET Method: path should not be empty')

        def decorator_get_func(func):
            func.__decorator__ = "GET"
            func.__decorator_path__ = path
            return func

        return decorator_get_func

    @classmethod
    def post(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('POST Method: path should be a string')
        if len(path) == 0:
            raise ValueError('POST Method: path should not be empty')

        def decorator_post_func(func):
            func.__decorator__ = "POST"
            func.__decorator_path__ = path
            return func

        return decorator_post_func

    @classmethod
    def put(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('PUT Method: path should be a string')
        if len(path) == 0:
            raise ValueError('PUT Method: path should not be empty')

        def decorator_put_func(func):
            func.__decorator__ = "PUT"
            func.__decorator_path__ = path
            return func

        return decorator_put_func

    @classmethod
    def delete(cls, path: str):
        if not isinstance(path, str):
            raise ValueError('DELETE Method: path should be a string')
        if len(path) == 0:
            raise ValueError('DELETE Method: path should not be empty')

        def decorator_delete_func(func):
            func.__decorator__ = "DELETE"
            func.__decorator_path__ = path
            return func

        return decorator_delete_func

    @classmethod
    def exception_advice(cls) -> callable:
        def decorator_advice_func(other_cls) -> type:
            if not isinstance(other_cls, type):
                raise TypeError('ExceptionAdvice can only be applied to classes')
            other_cls.__decorator__ = "ExceptionAdvice"
            return other_cls

        return decorator_advice_func

    @classmethod
    def throws_exception(cls, ex_type: type):
        if not isinstance(ex_type, type):
            raise TypeError("ThrowsException: argument 'ex' must be a type")

        def decorator_throws_exception_func(func) -> callable:
            func.__decorator__ = "ThrowsException"
            func.__decorator_params__ = ex_type
            return func

        return decorator_throws_exception_func

    @classmethod
    def request_interceptor(cls, interceptor_paths: set[str]) -> callable:
        if not isinstance(interceptor_paths, set):
            raise TypeError('RequestInterceptor: interceptor_paths must be a set')
        for interceptor_path in interceptor_paths:
            if not isinstance(interceptor_path, str):
                raise TypeError('RequestInterceptor: interceptor_paths must be a string set')

        def decorator_request_func(other_cls) -> type:
            if not isinstance(other_cls, type):
                raise TypeError('RequestInterceptor can only be applied to classes')
            other_cls.__decorator__ = "RequestInterceptor"
            other_cls.__decorator_params__ = interceptor_paths
            return other_cls

        return decorator_request_func

    @classmethod
    def interceptor_before(cls) -> callable:
        def decorator_request_func(func) -> callable:

            def interceptor_before_method(it_self: object, request: BaseHTTPRequestHandler) -> tuple[int, bool]:
                if not isinstance(request, BaseHTTPRequestHandler) and not isinstance(it_self, BaseHTTPRequestHandler):
                    raise ArgumentTypeError('InterceptorBefore: argument must be BaseHTTPRequestHandler Type')
                request.headers["X-Intercepted"] = "True"
                response_code, response_status = func(it_self, request)
                if not isinstance(response_code, int) or not isinstance(response_status, bool):
                    err: str = 'InterceptorBefore: return value must be (response_code: int, response_status: bool)'
                    raise ValueError(err)
                return response_code, response_status

            interceptor_before_method.__decorator__ = "InterceptorBefore"
            return interceptor_before_method

        return decorator_request_func

    @classmethod
    def interceptor_after(cls) -> callable:
        def decorator_request_func(func) -> callable:
            def interceptor_after_method(it_self: object, request: BaseHTTPRequestHandler) -> None:
                if not isinstance(request, BaseHTTPRequestHandler) and not isinstance(it_self, BaseHTTPRequestHandler):
                    raise ArgumentTypeError('InterceptorAfter: argument should be BaseHTTPRequestHandler Type')
                func(it_self, request)
                return None

            interceptor_after_method.__decorator__ = "InterceptorAfter"
            return interceptor_after_method

        return decorator_request_func


component = ContainerAnnotation.component
mapper = ContainerAnnotation.mapper
service = ContainerAnnotation.service
controller = ContainerAnnotation.controller
resource = ContainerAnnotation.resource
get = ContainerAnnotation.get
post = ContainerAnnotation.post
put = ContainerAnnotation.put
delete = ContainerAnnotation.delete
exception_advice = ContainerAnnotation.exception_advice
throws_exception = ContainerAnnotation.throws_exception
request_interceptor = ContainerAnnotation.request_interceptor
interceptor_before = ContainerAnnotation.interceptor_before
interceptor_after = ContainerAnnotation.interceptor_after
