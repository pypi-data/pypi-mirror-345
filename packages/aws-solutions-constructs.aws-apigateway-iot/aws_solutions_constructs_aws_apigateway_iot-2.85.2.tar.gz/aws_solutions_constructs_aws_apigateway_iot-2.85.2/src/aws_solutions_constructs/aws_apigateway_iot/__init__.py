r'''
# aws-apigateway-iot module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_apigateway_iot`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-apigateway-iot`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.apigatewayiot`|

## Overview

This AWS Solutions Construct implements an Amazon API Gateway REST API connected to AWS IoT pattern.

This construct creates a scalable HTTPS proxy between API Gateway and AWS IoT. This comes in handy when wanting to allow legacy devices that do not support the MQTT or MQTT/Websocket protocol to interact with the AWS IoT platform.

This implementation enables write-only messages to be published on given MQTT topics, and also supports shadow updates of HTTPS devices to allowed things in the device registry. It does not involve Lambda functions for proxying messages, and instead relies on direct API Gateway to AWS IoT integration which supports both JSON messages as well as binary messages.

Here is a minimal deployable pattern definition, note that the ATS endpoint for IoT must be used to avoid SSL certificate issues:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { ApiGatewayToIot } from '@aws-solutions-constructs/aws-apigateway-iot';

new ApiGatewayToIot(this, 'ApiGatewayToIotPattern', {
    iotEndpoint: 'a1234567890123-ats'
});
```

Python

```python
from aws_solutions_constructs.aws_apigateway_iot import ApiGatewayToIot
from aws_cdk import Stack
from constructs import Construct

ApiGatewayToIot(self, 'ApiGatewayToIotPattern',
    iot_endpoint='a1234567890123-ats'
)
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awsconstructs.services.apigatewayiot.*;

new ApiGatewayToIot(this, "ApiGatewayToIotPattern", new ApiGatewayToIotProps.Builder()
        .iotEndpoint("a1234567890123-ats")
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|iotEndpoint|`string`|The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g a1234567890123-ats). Note that this must point to the ATS endpoint to avoid SSL certificate trust issues. The endpoint can be retrieved by running `aws iot describe-endpoint --endpoint-type iot:Data-ATS`.|
|apiGatewayCreateApiKey?|`boolean`|If set to `true`, an API Key is created and associated to a UsagePlan. User should specify `x-api-key` header while accessing RestApi. Default value set to `false`|
|apiGatewayExecutionRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html)|IAM Role used by the API Gateway to access AWS IoT. If not specified, a default role is created with wildcard ('*') access to all topics and things.|
|apiGatewayProps?|[`api.restApiProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.RestApiProps.html)|Optional user-provided props to override the default props for the API Gateway.|
|createUsagePlan?|boolean|Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true. @default - true (to match legacy behavior)|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|apiGatewayRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway.|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon API Gateway

* Deploy an edge-optimized API Endpoint
* Creates API Resources with `POST` Method to publish messages to IoT Topics
* Creates API Resources with `POST` Method to publish messages to ThingShadow & NamedShadows
* Enable CloudWatch logging for API Gateway
* Configure IAM role for API Gateway with access to all topics and things
* Set the default authorizationType for all API methods to IAM
* Enable X-Ray Tracing
* Creates a UsagePlan and associates to `prod` stage

Below is a description of the different resources and methods exposed by the API Gateway after deploying the Construct.

|Method         | Resource              | Query parameter(s) |  Return code(s)   |  Description|
|-------------- | --------------------- | ------------------ | ----------------- | -----------------|
|  **POST**     |  `/message/<topics>`  |      **qos**       |   `200/403/500`   | By calling this endpoint, you need to pass the topics on which you would like to publish (e.g `/message/device/foo`).|
|  **POST**     | `/shadow/<thingName>` |      **None**      |   `200/403/500`   | This route allows to update the shadow document of a thing, given its `thingName` using Unnamed (classic) shadow type. The body shall comply with the standard shadow structure comprising a `state` node and associated `desired` and `reported` nodes.|
|  **POST**     | `/shadow/<thingName>/<shadowName>` |      **None**      |   `200/403/500`   | This route allows to update the named shadow document of a thing, given its `thingName` and the `shadowName` using the Named shadow type. The body shall comply with the standard shadow structure comprising a `state` node and associated `desired` and `reported` nodes.|

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8


class ApiGatewayToIot(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-apigateway-iot.ApiGatewayToIot",
):
    '''
    :summary: The ApiGatewayIot class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        iot_endpoint: builtins.str,
        api_gateway_create_api_key: typing.Optional[builtins.bool] = None,
        api_gateway_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param iot_endpoint: The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g ab123cdefghij4l-ats). Added as AWS Subdomain to the Integration Request. Note that this must reference the ATS endpoint to avoid SSL certificate trust issues. Default: - None.
        :param api_gateway_create_api_key: Creates an api key and associates to usage plan if set to true. Default: - false
        :param api_gateway_execution_role: The IAM role that is used by API Gateway to publish messages to IoT topics and Thing shadows. Default: - An IAM role with iot:Publish access to all topics (topic/*) and iot:UpdateThingShadow access to all things (thing/*) is created.
        :param api_gateway_props: Optional user-provided props to override the default props for the API. Default: - Default props are used.
        :param create_usage_plan: Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true Default: - true (to match legacy behavior)
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the ApiGatewayIot class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e924fb0cf81b109b48a204074c76b3f0589533998633acfa966ff106a85324c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiGatewayToIotProps(
            iot_endpoint=iot_endpoint,
            api_gateway_create_api_key=api_gateway_create_api_key,
            api_gateway_execution_role=api_gateway_execution_role,
            api_gateway_props=api_gateway_props,
            create_usage_plan=create_usage_plan,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayRole")
    def api_gateway_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "apiGatewayRole"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-apigateway-iot.ApiGatewayToIotProps",
    jsii_struct_bases=[],
    name_mapping={
        "iot_endpoint": "iotEndpoint",
        "api_gateway_create_api_key": "apiGatewayCreateApiKey",
        "api_gateway_execution_role": "apiGatewayExecutionRole",
        "api_gateway_props": "apiGatewayProps",
        "create_usage_plan": "createUsagePlan",
        "log_group_props": "logGroupProps",
    },
)
class ApiGatewayToIotProps:
    def __init__(
        self,
        *,
        iot_endpoint: builtins.str,
        api_gateway_create_api_key: typing.Optional[builtins.bool] = None,
        api_gateway_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''The properties for the ApiGatewayIot class.

        :param iot_endpoint: The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g ab123cdefghij4l-ats). Added as AWS Subdomain to the Integration Request. Note that this must reference the ATS endpoint to avoid SSL certificate trust issues. Default: - None.
        :param api_gateway_create_api_key: Creates an api key and associates to usage plan if set to true. Default: - false
        :param api_gateway_execution_role: The IAM role that is used by API Gateway to publish messages to IoT topics and Thing shadows. Default: - An IAM role with iot:Publish access to all topics (topic/*) and iot:UpdateThingShadow access to all things (thing/*) is created.
        :param api_gateway_props: Optional user-provided props to override the default props for the API. Default: - Default props are used.
        :param create_usage_plan: Whether to create a Usage Plan attached to the API. Must be true if apiGatewayProps.defaultMethodOptions.apiKeyRequired is true Default: - true (to match legacy behavior)
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        '''
        if isinstance(api_gateway_props, dict):
            api_gateway_props = _aws_cdk_aws_apigateway_ceddda9d.RestApiProps(**api_gateway_props)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8700595a6a6afd7bc80184c79201387ce9c5cc241bfb91bc3cf126abc3e944c8)
            check_type(argname="argument iot_endpoint", value=iot_endpoint, expected_type=type_hints["iot_endpoint"])
            check_type(argname="argument api_gateway_create_api_key", value=api_gateway_create_api_key, expected_type=type_hints["api_gateway_create_api_key"])
            check_type(argname="argument api_gateway_execution_role", value=api_gateway_execution_role, expected_type=type_hints["api_gateway_execution_role"])
            check_type(argname="argument api_gateway_props", value=api_gateway_props, expected_type=type_hints["api_gateway_props"])
            check_type(argname="argument create_usage_plan", value=create_usage_plan, expected_type=type_hints["create_usage_plan"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "iot_endpoint": iot_endpoint,
        }
        if api_gateway_create_api_key is not None:
            self._values["api_gateway_create_api_key"] = api_gateway_create_api_key
        if api_gateway_execution_role is not None:
            self._values["api_gateway_execution_role"] = api_gateway_execution_role
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if create_usage_plan is not None:
            self._values["create_usage_plan"] = create_usage_plan
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def iot_endpoint(self) -> builtins.str:
        '''The AWS IoT endpoint subdomain to integrate the API Gateway with (e.g ab123cdefghij4l-ats). Added as AWS Subdomain to the Integration Request. Note that this must reference the ATS endpoint to avoid SSL certificate trust issues.

        :default: - None.
        '''
        result = self._values.get("iot_endpoint")
        assert result is not None, "Required property 'iot_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_gateway_create_api_key(self) -> typing.Optional[builtins.bool]:
        '''Creates an api key and associates to usage plan if set to true.

        :default: - false
        '''
        result = self._values.get("api_gateway_create_api_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def api_gateway_execution_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that is used by API Gateway to publish messages to IoT topics and Thing shadows.

        :default: - An IAM role with iot:Publish access to all topics (topic/*) and iot:UpdateThingShadow access to all things (thing/*) is created.
        '''
        result = self._values.get("api_gateway_execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def api_gateway_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps]:
        '''Optional user-provided props to override the default props for the API.

        :default: - Default props are used.
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps], result)

    @builtins.property
    def create_usage_plan(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a Usage Plan attached to the API.

        Must be true if
        apiGatewayProps.defaultMethodOptions.apiKeyRequired is true

        :default: - true (to match legacy behavior)
        '''
        result = self._values.get("create_usage_plan")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToIotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToIot",
    "ApiGatewayToIotProps",
]

publication.publish()

def _typecheckingstub__2e924fb0cf81b109b48a204074c76b3f0589533998633acfa966ff106a85324c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    iot_endpoint: builtins.str,
    api_gateway_create_api_key: typing.Optional[builtins.bool] = None,
    api_gateway_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8700595a6a6afd7bc80184c79201387ce9c5cc241bfb91bc3cf126abc3e944c8(
    *,
    iot_endpoint: builtins.str,
    api_gateway_create_api_key: typing.Optional[builtins.bool] = None,
    api_gateway_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
