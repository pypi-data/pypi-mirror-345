# @Coding: UTF-8
# @Time: 2024/9/22 17:13
# @Author: xieyang_ls
# @Filename: __init__.py.py

from pyutils_spirit.spirit_container.annotation import (component,
                                                        mapper,
                                                        service,
                                                        controller,
                                                        resource,
                                                        get, post, put, delete,
                                                        exception_advice,
                                                        throws_exception,
                                                        request_interceptor,
                                                        interceptor_before,
                                                        interceptor_after)

from pyutils_spirit.spirit_container.multipart_file import MultipartFile

from pyutils_spirit.spirit_container.request_result import Result

from pyutils_spirit.spirit_container.spirit_application import SpiritApplication

__all__ = ["component",
           "mapper",
           "service",
           "controller",
           "resource",
           "get",
           "post",
           "put",
           "delete",
           "exception_advice",
           "throws_exception",
           "request_interceptor",
           "interceptor_before",
           "interceptor_after",
           'MultipartFile',
           'Result',
           "SpiritApplication"]
