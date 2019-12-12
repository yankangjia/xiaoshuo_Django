from django.http import JsonResponse


class HttpCode:
    ok = 200                # 成功
    paramserror = 400       # 参数错误
    unauth = 401            # 没有授权
    methoderror = 405       # 方法错误
    servererror = 500       # 服务器内部错误


def result(code=HttpCode.ok,message="",data=None,kwargs=None):
    json_dict = {"code":code,"message":message,"data":data}
    if kwargs and isinstance(kwargs,dict) and kwargs.keys():
        json_dict.update(kwargs)
    return JsonResponse(json_dict)

def ok():
    return result()

def params_error(message="",data=None):
    return result(code=HttpCode.paramserror,message=message,data=data)

def unauth(message="",data=None):
    return result(code=HttpCode.unauth,message=message,data=data)

def method_error(message="",data=None):
    return result(code=HttpCode.methoderror,message=message,data=data)

def server_error(message="",data=None):
    return result(code=HttpCode.servererror,message=message,data=data)