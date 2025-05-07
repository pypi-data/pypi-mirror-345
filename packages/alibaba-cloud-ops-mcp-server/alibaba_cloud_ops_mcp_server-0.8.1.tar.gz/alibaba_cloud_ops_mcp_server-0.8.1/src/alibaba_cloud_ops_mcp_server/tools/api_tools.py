import os
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field
import logging

import inspect
import types
from dataclasses import make_dataclass, field
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient
from alibaba_cloud_ops_mcp_server.alibabacloud.api_meta_client import ApiMetaClient


type_map = {
    'string': str,
    'integer': int,
    'boolean': bool,
    'array': list,
    'object': dict,
    'number': float
}


def create_client(service: str, region_id: str) -> OpenApiClient:
    config = open_api_models.Config(
        access_key_id=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        access_key_secret=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        security_token=os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN'),
        user_agent='alibaba-cloud-ops-mcp-server',
    )
    if isinstance(service, str):
        service = service.lower()
    config.endpoint = f'{service}.{region_id}.aliyuncs.com'
    return OpenApiClient(config)


def _tools_api_call(service: str, api: str, parameters: dict, ctx: Context):
    service = service.lower()
    api_meta, _ = ApiMetaClient.get_api_meta(service, api)
    version = ApiMetaClient.get_service_version(service)
    method = 'POST' if api_meta.get('methods', [])[0] == 'post' else 'GET'
    path = api_meta.get('path', '/')
    style = ApiMetaClient.get_service_style(service)
    req = open_api_models.OpenApiRequest(
        query=OpenApiUtilClient.query(parameters)
    )
    params = open_api_models.Params(
        action=api,
        version=version,
        protocol='HTTPS',
        pathname=path,
        method=method,
        auth_type='AK',
        style=style,
        req_body_type='formData',
        body_type='json'
    )
    client = create_client(service, parameters.get('RegionId', 'cn-hangzhou'))
    runtime = util_models.RuntimeOptions()
    return client.call_api(params, req, runtime)


def _create_parameter_schema(fields: dict):
    return make_dataclass("ParameterSchema", [(name, type_, value) for name, (type_, value) in fields.items()])


def _create_function_schemas(service, api, api_meta):
    schemas = {}
    schemas[api] = {}
    parameters = api_meta.get('parameters', [])
    for parameter in parameters:
        name = parameter.get('name')
        # TODO 目前忽略了带'.'的参数
        if '.' in name:
            continue
        schema = parameter.get('schema', '')
        description = schema.get('description', '')
        example = schema.get('example', '')
        type_ = schema.get('type', '')
        description = f'{description} 请注意，提供参数要严格按照参数的类型和参数示例的提示，如果提到参数为String，且为一个 JSON 数组字符串，应在数组内使用单引号包裹对应的参数以避免转义问题，并在最外侧用双引号包裹以确保其是字符串，否则可能会导致参数解析错误。参数类型: {type_},参数示例：{example}'
        required = schema.get('required', False)
        python_type = type_map.get(type_, str)
        field_info = (
            python_type,
            field(
                default=None,
                metadata={'description': description, 'required': required}
            )
        )
        schemas[api][name] = field_info
    if 'RegionId' not in schemas[api]:
        schemas[api]['RegionId'] = (
            str,
            field(
                default=None,
                metadata={'description': '地域ID', 'required': False}
            )
        )
    return schemas


def _create_tool_function_with_signature(service: str, function_name: str, fields: dict, description: str):
    """
    Dynamically creates a lambda function with a custom signature based on the provided fields.
    """
    parameters = []
    annotations = {}
    defaults = {}

    for name, (type_, field_info) in fields.items():
        field_description = field_info.metadata.get('description', '')
        is_required = field_info.metadata.get('required', False)
        default_value = field_info.default if not is_required else ...

        field_default = Field(default=default_value, description=field_description)
        parameters.append(inspect.Parameter(
            name=name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=field_default,
            annotation=type_
        ))
        annotations[name] = type_
        defaults[name] = field_default

    signature = inspect.Signature(parameters)

    def func_code(*args, **kwargs):
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        return _tools_api_call(
            service=service,
            api=function_name,
            parameters=bound_args.arguments,
            ctx=None
        )

    func = types.FunctionType(
        func_code.__code__,
        globals(),
        function_name,
        None,
        func_code.__closure__
    )
    func.__signature__ = signature
    func.__annotations__ = annotations
    func.__defaults__ = tuple(defaults.values())
    func.__doc__ = description

    return func


def _create_and_decorate_tool(mcp: FastMCP, service: str, api: str):
    """Create a tool function for an AlibabaCloud openapi."""
    api_meta, _ = ApiMetaClient.get_api_meta(service, api)
    fields = _create_function_schemas(service, api, api_meta).get(api, {})
    description = api_meta.get('summary', '')
    dynamic_lambda = _create_tool_function_with_signature(service, api, fields, description)
    decorated_function = mcp.tool(name=api)(dynamic_lambda)

    return decorated_function

def create_api_tools(mcp: FastMCP, config:dict):
    for service_code, apis in config.items():
        for api_name in apis:
            _create_and_decorate_tool(mcp, service_code, api_name)
