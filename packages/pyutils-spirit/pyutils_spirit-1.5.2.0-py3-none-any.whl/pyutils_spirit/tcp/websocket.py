# @Coding: UTF-8
# @Time: 2024/9/20 12:29
# @Author: xieyang_ls
# @Filename: websocket.py

import time

import socket

import base64

import hashlib

import inspect

from abc import ABC
from typing import Any

from pyutils_spirit.style import draw_websocket_banner

from logging import info, basicConfig, INFO, exception

from pyutils_spirit.concurrent_thread.thread_holder import ThreadHolder

from pyutils_spirit.concurrent_thread.thread_executor import ThreadExecutor

basicConfig(level=INFO)


class WebSocket(ABC):
    __socket_server: socket.socket = None

    __listener_count = None

    __buffer_size: int = None

    __websocket_end_points: set[type] = None

    __executor: ThreadExecutor = None

    container: ThreadHolder[str, Any] = None

    __close_signature = None

    @classmethod
    def __start_server(cls, host, port, other_cls):
        cls.__socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.__listener_count = 100000
        cls.__buffer_size = 4096
        cls.__websocket_server_class = other_cls
        cls.__executor = ThreadExecutor(executor_count=cls.__listener_count + 1)
        cls.container = ThreadHolder.constructor()
        cls.__socket_server.bind((host, port))
        cls.__socket_server.listen(cls.__listener_count)
        cls.__executor.execute(cls.__listener_connection)
        cls.__close_signature = ""
        info(f"WebSocket Server listening on ws://{host}:{port}")

    class Session:
        __socket: socket.socket = None

        __address: tuple[str, int] = None

        __buffer_size: int = None

        __is_connected: bool = None

        __headers: dict = None

        __params: dict = None

        __start_connected_timer: float = None

        __close_connected_timer: float = None

        def __init__(self,
                     socket_client: socket.socket,
                     address: tuple[str, int],
                     headers: dict,
                     params: dict,
                     is_connected: bool = True,
                     buffer_size: int = 4096):
            self.__socket = socket_client
            self.__address = address
            self.__headers = headers
            self.__params = params
            self.__is_connected = is_connected
            self.__buffer_size = buffer_size
            self.__start_connected_timer = time.time()

        def get_socket_client(self) -> socket.socket:
            return self.__socket

        def get_is_connected(self) -> bool:
            return self.__is_connected

        def get_address(self):
            if self.__address is None:
                self.__address = self.__socket.getpeername()
            return self.__address

        def get_headers(self) -> dict:
            if self.__headers is not None:
                return self.__headers  # 已缓存的 headers 则直接返回

        def get_params(self) -> dict:
            return self.__params

        def send_message(self, message: str, encoding: str = "utf-8", opcode: int = 0x1) -> None:
            try:
                # 验证操作码
                if opcode not in (0x1, 0x2):
                    raise ValueError("Opcode must be 0x1 (text) or 0x2 (binary)")
                # 编码消息
                message_bytes = message.encode(encoding)
                fin = 0x80  # FIN=1（不分片）
                mask_bit = 0x00  # 服务器必须不掩码
                # 构造帧头
                header = bytearray()
                payload_len = len(message_bytes)
                # 处理长度字段
                if payload_len <= 125:
                    header += bytes([fin | opcode, payload_len | mask_bit])
                elif payload_len <= 65535:
                    header += bytes([fin | opcode, 126 | mask_bit])
                    header += payload_len.to_bytes(length=2, byteorder='big', signed=False)
                else:
                    header += bytes([fin | opcode, 127 | mask_bit])
                    header += payload_len.to_bytes(length=8, byteorder='big', signed=False)
                # 发送完整帧
                self.__socket.send(header + message_bytes)
            except (UnicodeEncodeError, ValueError) as e:
                exception(f"Encoding/Validation error: {str(e)}")
            except Exception as e:
                exception(f"Send error: {str(e)}")

        def __send_close_frame(self, code: int, reason: str) -> None:
            payload = code.to_bytes(length=2, byteorder='big', signed=False)
            if reason:
                payload += reason.encode('utf-8')
            # 构造帧头
            fin = 0x80
            opcode = 0x08  # 关闭帧
            length = len(payload)
            if length <= 125:
                frame = bytes([fin | opcode, length]) + payload
            elif length <= 65535:
                frame = bytes([fin | opcode, 126]) + length.to_bytes(length=2, byteorder='big') + payload
            else:
                frame = bytes([fin | opcode, 127]) + length.to_bytes(length=8, byteorder='big') + payload
            self.__socket.send(frame)

        def close(self, close_code: int = 1000, reason: str = "See you again~~") -> None:
            if self.__is_connected is True:
                self.__is_connected = False
                self.__close_connected_timer = time.time()
                info(f"Disconnecting Session: {self}")
                self.__send_close_frame(code=close_code, reason=reason)
                self.__socket.close()
                __endpoint = WebSocket.container.remove_holder(key=str(self.__address))
                __onclose: callable = __endpoint.ws_funcs["onclose"]
                if __onclose is not None:
                    __onclose(self=__endpoint, session=self)
                session_id = id(self.__socket)
                if session_id in __endpoint.message_buffer:
                    del __endpoint.message_buffer[session_id]
                if self.__socket in __endpoint.partial_data:
                    del __endpoint.partial_data[self.__socket]

        def __str__(self) -> str:
            if self.__is_connected:
                connected_timer: str = f"current_connected_timer={time.time() - self.__start_connected_timer}"
            else:
                connected_timer = f"total_connected_timer={self.__close_connected_timer - self.__start_connected_timer}"
            return ("{" + f"socket={self.__socket}, " +
                    f"address={self.__address}, " +
                    f"{connected_timer}" + "}")

    @classmethod
    def __handshaking(cls, socket_client: socket.socket, ws_headers: dict) -> bool:
        # WebSocket 握手
        try:
            # 检查必要字段是否存在
            ws_key = ws_headers.get("Sec-WebSocket-Key", "")
            if not ws_key:
                ws_key = ws_headers.get("sec-websocket-key", "")
                if not ws_key:
                    raise ValueError("Missing Sec-WebSocket-Key")

            # 验证 WebSocket 版本
            ws_version = ws_headers.get("Sec-WebSocket-Version", "13")
            if ws_version != "13":
                response = (
                    "HTTP/1.1 426 Upgrade Required\r\n"
                    "Sec-WebSocket-Version: 13\r\n\r\n"
                )
                socket_client.send(response.encode())
                return False

            # 生成 Accept Key
            magic_guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            accept_key = base64.b64encode(
                hashlib.sha1((ws_key + magic_guid).encode()).digest()
            ).decode()

            # 构建响应头（增加版本确认）
            response_headers = [
                "HTTP/1.1 101 Switching Protocols",
                "Upgrade: websocket",
                "Connection: Upgrade",
                f"Sec-WebSocket-Accept: {accept_key}",
                "Sec-WebSocket-Version: 13",  # 明确返回支持的版本
            ]

            # 发送握手响应
            response = "\r\n".join(response_headers) + "\r\n\r\n"
            socket_client.send(response.encode())
            return True

        except (KeyError, ValueError) as e:
            # 处理无效请求
            exception(f"Key / Value Error: {e}")
            error_response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            socket_client.send(error_response.encode())
            return False

        except Exception as e:
            # 处理其他异常（如连接中断）
            exception(f"Handshake error: {str(e)}")
            return False

    @classmethod
    def __listener_connection(cls) -> None:
        while True:
            try:
                socket_client, addr = cls.__socket_server.accept()
                # 缓冲区分块接收，直到遇到 \r\n\r\n
                header_data: bytes | None = None

                buffer = bytearray()
                while True:
                    chunk = socket_client.recv(cls.__buffer_size)  # 每次接收 4KB
                    if not chunk:  # 连接关闭
                        break
                    buffer.extend(chunk)
                    if b"\r\n\r\n" in buffer:
                        # 找到头部结束位置并截断
                        header_end = buffer.index(b"\r\n\r\n")
                        header_data = buffer[:header_end]
                        break
                try:
                    # 解码并解析头部
                    ws_endpoint_cls: type | None = None
                    ws_headers: dict[str, str] = {}
                    params: dict[str, str | int] = {}
                    header_str = header_data.decode("utf-8")
                    lines = header_str.split("\r\n")
                    for end_point_cls in cls.__websocket_end_points:
                        signature = getattr(end_point_cls, "__decorator_signature__")
                        paths = lines[0].split(signature)
                        if len(paths) == 2 and paths[0][-1] == " " and paths[1][0] in (" ", "?"):
                            ws_endpoint_cls = end_point_cls
                            break
                    if ws_endpoint_cls is None:
                        ex_msg = f"Error: WebSocket URL({lines[0].split()[1]}) cannot match endpoint signature"
                        ex_str = (
                            "HTTP/1.1 400 Bad Request\r\n"
                            "Content-Type: text/plain\r\n"
                            "Connection: close({})\r\n\r\n"
                        ).format(ex_msg)
                        socket_client.send(ex_str.encode("utf-8"))
                        socket_client.close()
                        raise (ValueError(f"{ex_msg}"))
                    arguments = lines[0].split()[1].split("?")
                    if len(arguments) > 1:
                        for param in arguments[1].split("&"):
                            key, value = param.split(sep="=", maxsplit=1)
                            params[key] = value
                    for line in lines[1:]:  # 跳过请求行（如 GET / HTTP/1.1）
                        if ": " in line:
                            key, value = line.split(sep=": ", maxsplit=1)
                            ws_headers[key] = value
                except UnicodeDecodeError as e:
                    # 处理编码错误
                    exception(f"Header decoding error: {e}")
                    continue
                except ValueError as e:
                    # 处理键值对解析错误
                    exception(f"Invalid header format: {e}")
                    continue
                if cls.__handshaking(socket_client=socket_client, ws_headers=ws_headers):
                    __endpoint = ws_endpoint_cls()
                    cls.container.set_holder(key=str(addr), value=__endpoint)
                    session = cls.Session(socket_client=socket_client,
                                          address=addr,
                                          headers=ws_headers,
                                          params=params)
                    info(f"Session: {session} connection successful")
                    cls.__executor.execute(task=cls.__listener_message, end_point=__endpoint, session=session)
                    __onopen: callable = __endpoint.ws_funcs["onopen"]
                    if __onopen is not None:
                        __onopen(self=__endpoint, session=session)
            except Exception as e:
                exception(e)

    @classmethod
    def __receive_message(cls, end_point, session: Session):
        # 接收消息
        socket_client: socket.socket = session.get_socket_client()
        session_id = id(socket_client)
        data = end_point.partial_data.get(socket_client, b'') + socket_client.recv(cls.__buffer_size)

        try:
            while len(data) >= 2:
                # 1. 解析帧头
                fin = (data[0] & 0x80) >> 7
                rsv = (data[0] & 0x70) >> 4
                opcode = data[0] & 0x0F
                masked = (data[1] & 0x80) >> 7
                payload_len = data[1] & 0x7F
                # 2. 协议合规性校验
                if rsv != 0:
                    raise ValueError("RSV位违规")
                if not masked:  # 所有客户端帧必须掩码
                    raise ValueError("未掩码数据帧")
                # 3. 解析payload长度和掩码
                mask_start = 2
                if payload_len == 126:
                    if len(data) < 4:
                        break
                    payload_len = int.from_bytes(data[2:4], 'big')
                    mask_start = 4
                elif payload_len == 127:
                    if len(data) < 10:
                        break
                    if (data[2] & 0x80) != 0:
                        raise ValueError("无效长度")
                    payload_len = int.from_bytes(data[2:10], 'big')
                    mask_start = 10
                # 4. 检查数据完整性
                if len(data) < mask_start + 4 + payload_len:
                    break
                # 5. 解码payload
                masks = data[mask_start:mask_start + 4]
                payload = data[mask_start + 4:mask_start + 4 + payload_len]
                decoded = bytes([payload[i] ^ masks[i % 4] for i in range(payload_len)])
                # 6. 处理控制帧
                if opcode in (0x8, 0x9, 0xA):
                    if not fin:
                        raise ValueError("控制帧不能分片")
                    if payload_len > 125:
                        raise ValueError("控制帧负载过长")
                    if opcode == 0x8:  # Close帧
                        return session.close()
                    elif opcode == 0x9:  # Ping帧
                        # 发送Pong帧，携带解码后的数据
                        header = bytearray([0x8A])  # FIN=1, opcode=0xA
                        if len(decoded) <= 125:
                            header.append(len(decoded))
                        elif len(decoded) <= 0xFFFF:
                            header.extend([126, *len(decoded).to_bytes(length=2, byteorder='big')])
                        else:
                            header.extend([127, *len(decoded).to_bytes(length=8, byteorder='big')])
                        socket_client.send(bytes(header) + decoded)
                        # 继续处理剩余数据
                        data = data[mask_start + 4 + payload_len:]
                        continue
                    elif opcode == 0xA:  # Pong帧，忽略
                        data = data[mask_start + 4 + payload_len:]
                        continue
                # 7. 处理数据帧
                if session_id not in end_point.message_buffer:
                    end_point.message_buffer[session_id] = {'fragments': [], 'opcode': opcode}
                else:
                    if opcode != 0x0:
                        raise ValueError("分片连续性错误")
                end_point.message_buffer[session_id]['fragments'].append(decoded)
                if fin:
                    full_data = b''.join(end_point.message_buffer[session_id]['fragments'])
                    original_opcode = end_point.message_buffer[session_id]['opcode']
                    del end_point.message_buffer[session_id]
                    # 处理数据
                    if original_opcode == 0x1:
                        try:
                            result = full_data.decode('utf-8')
                        except UnicodeDecodeError as e:
                            return session.close(close_code=60001, reason=str(e))
                    else:
                        result = full_data
                    data = data[mask_start + 4 + payload_len:]
                    end_point.partial_data[socket_client] = data
                    return result
                else:
                    data = data[mask_start + 4 + payload_len:]
        except (ConnectionResetError, ValueError) as e:
            exception(f"协议错误: {e}")
            session.close(close_code=60001, reason=str(e))
        finally:
            end_point.partial_data[socket_client] = data
        return None

    @classmethod
    def __listener_message(cls, end_point, session: Session) -> None:
        while session.get_is_connected():
            try:
                message: str = cls.__receive_message(end_point=end_point, session=session)
                if message is None:
                    continue
                elif message == "ping":
                    session.send_message("pong")
                elif message == cls.__close_signature:
                    session.close()
                else:
                    __onmessage: callable = end_point.ws_funcs["onmessage"]
                    if __onmessage is not None:
                        __onmessage(self=end_point, message=message)
            except Exception as e:
                exception(e)
                __onerror: callable = end_point.ws_funcs["onerror"]
                if __onerror is not None:
                    try:
                        __onerror(self=end_point, session=session, ex=e)
                    except Exception as e:
                        exception(e)

    @classmethod
    def websocket_server(cls, host: str, port: int) -> callable:

        def decorator_handler(other_cls) -> type:
            draw_websocket_banner()
            cls.__start_server(host, port, other_cls)
            other_cls.__decorator__ = "WebSocketServer"
            other_cls.__decorator_params__ = {
                "host": host,
                "port": port
            }
            return other_cls

        return decorator_handler

    @classmethod
    def endpoint(cls, signature: str) -> callable:
        if not isinstance(signature, str):
            raise TypeError("the signature must be a string")

        def decorator_handler(other_cls) -> type:
            other_cls.__decorator__ = "WebSocketServerEndPoint"
            other_cls.__decorator_signature__ = signature
            other_cls.partial_data = {}
            other_cls.message_buffer = {}
            ws_funcs: dict[str, callable] = {
                "onopen": None,
                "onmessage": None,
                "onerror": None,
                "onclose": None
            }
            for method_name, method in inspect.getmembers(other_cls):
                decorator = getattr(method, "__decorator__", None)
                if decorator in ["onopen", "onmessage", "onerror", "onclose"]:
                    ws_funcs[decorator] = method
            other_cls.ws_funcs = ws_funcs
            if cls.__websocket_end_points is None:
                cls.__websocket_end_points = set()
            cls.__websocket_end_points.add(other_cls)
            return other_cls

        return decorator_handler

    @classmethod
    def onopen(cls) -> callable:
        def decorator_handler(func) -> None:
            func.__decorator__ = "onopen"
            cls.__onopen_func = func
            return func

        return decorator_handler

    @classmethod
    def onmessage(cls) -> callable:
        def decorator_handler(func) -> None:
            func.__decorator__ = "onmessage"
            cls.__onmessage_func = func
            return func

        return decorator_handler

    @classmethod
    def onclose(cls) -> callable:
        def decorator_handler(func) -> None:
            func.__decorator__ = "onclose"
            cls.__onclose_func = func
            return func

        return decorator_handler

    @classmethod
    def onerror(cls) -> callable:
        def decorator_handler(func) -> None:
            func.__decorator__ = "onerror"
            cls.__onerror_func = func
            return func

        return decorator_handler


websocket_server = WebSocket.websocket_server
endpoint = WebSocket.endpoint
Session = WebSocket.Session
onopen = WebSocket.onopen
onmessage = WebSocket.onmessage
onclose = WebSocket.onclose
onerror = WebSocket.onerror
