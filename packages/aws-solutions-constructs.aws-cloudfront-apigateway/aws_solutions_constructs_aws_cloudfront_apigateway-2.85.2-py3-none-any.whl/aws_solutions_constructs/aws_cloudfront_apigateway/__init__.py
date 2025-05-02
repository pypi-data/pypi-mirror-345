r'''
# aws-cloudfront-apigateway module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_cloudfront_apigateway`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-cloudfront-apigateway`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.cloudfrontapigateway`|

## Overview

This AWS Solutions Construct implements an AWS CloudFront fronting an Amazon API Gateway REST API.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { CloudFrontToApiGateway } from '@aws-solutions-constructs/aws-cloudfront-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as api from 'aws-cdk-lib/aws-apigateway';

const lambdaProps: lambda.FunctionProps = {
  code: lambda.Code.fromAsset(`lambda`),
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler'
};

const lambdafunction = new lambda.Function(this, 'LambdaFunction', lambdaProps);

const apiGatewayProps: api.LambdaRestApiProps = {
  handler: lambdafunction,
  endpointConfiguration: {
    types: [api.EndpointType.REGIONAL]
  },
  defaultMethodOptions: {
    authorizationType: api.AuthorizationType.NONE
  }
};

const apiGateway = new api.LambdaRestApi(this, 'LambdaRestApi', apiGatewayProps);

new CloudFrontToApiGateway(this, 'test-cloudfront-apigateway', {
  existingApiGatewayObj: apiGateway
});
```

Python

```python
from aws_solutions_constructs.aws_cloudfront_apigateway import CloudFrontToApiGateway
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as api,
    Stack
)
from constructs import Construct

lambda_function = _lambda.Function(self, 'LambdaFunction',
                                    code=_lambda.Code.from_asset(
                                        'lambda'),
                                    runtime=_lambda.Runtime.PYTHON_3_11,
                                    handler='index.handler')

api_gateway = api.LambdaRestApi(self, 'LambdaRestApi',
                                handler=lambda_function,
                                endpoint_configuration=api.EndpointConfiguration(
                                    types=[api.EndpointType.REGIONAL]
                                ),
                                default_method_options=api.MethodOptions(
                                    authorization_type=api.AuthorizationType.NONE
                                ))

CloudFrontToApiGateway(self, 'test-cloudfront-apigateway',
                        existing_api_gateway_obj=api_gateway
                        )
```

Java

```java
import software.constructs.Construct;
import java.util.List;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.services.lambda.*;
import software.amazon.awscdk.services.lambda.Runtime;
import software.amazon.awscdk.services.apigateway.*;
import software.amazon.awsconstructs.services.cloudfrontapigateway.*;

final Function lambdaFunction = Function.Builder.create(this, "IndexHandler")
        .runtime(Runtime.NODEJS_20_X)
        .code(Code.fromAsset("lambda"))
        .handler("index.handler")
        .build();

final LambdaRestApi apiGateway = LambdaRestApi.Builder.create(this, "myapi")
        .handler(lambdaFunction)
        .endpointConfiguration(new EndpointConfiguration.Builder()
                .types(List.of(EndpointType.REGIONAL))
                .build())
        .build();

new CloudFrontToApiGateway(this, "test-cloudfront-apigateway", new CloudFrontToApiGatewayProps.Builder()
        .existingApiGatewayObj(apiGateway)
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingApiGatewayObj|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.RestApi.html)|The regional API Gateway that will be fronted with the CloudFront|
|cloudFrontDistributionProps?|[`cloudfront.DistributionProps \| any`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront.DistributionProps.html)|Optional user provided props to override the default props for CloudFront Distribution|
|insertHttpSecurityHeaders?|`boolean`|Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from CloudFront|
| responseHeadersPolicyProps?   | [`cloudfront.ResponseHeadersPolicyProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront.ResponseHeadersPolicyProps.html) | Optional user provided configuration that cloudfront applies to all http responses.|
|cloudFrontLoggingBucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.BucketProps.html)|Optional user provided props to override the default props for the CloudFront Logging Bucket.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|cloudFrontWebDistribution|[`cloudfront.Distribution`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront.Distribution.html)|Returns an instance of cloudfront.Distribution created by the construct|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|cloudFrontFunction?|[`cloudfront.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront.Function.html)|Returns an instance of the Cloudfront function created by the pattern.|
|cloudFrontLoggingBucket|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-s3-readme.html)|Returns an instance of the logging bucket for CloudFront Distribution.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon CloudFront

* Configure Access logging for CloudFront Distribution
* Enable automatic injection of best practice HTTP security headers in all responses from CloudFront Distribution

### Amazon API Gateway

* User provided API Gateway object is used as-is
* Enable X-Ray Tracing

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
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class CloudFrontToApiGateway(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-cloudfront-apigateway.CloudFrontToApiGateway",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        existing_api_gateway_obj: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_api_gateway_obj: Existing instance of api.RestApi object. Default: - None
        :param cloud_front_distribution_props: Optional user provided props to override the default props. Default: - Default props are used
        :param cloud_front_logging_bucket_props: Optional user provided props to override the default props for the CloudFront Logging Bucket. Default: - Default props are used
        :param insert_http_security_headers: Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront. Turning this on will inject default headers and is mutually exclusive with passing custom security headers via the responseHeadersPolicyProps parameter. Default: - true
        :param response_headers_policy_props: Optional user provided configuration that cloudfront applies to all http responses. Can be used to pass a custom ResponseSecurityHeadersBehavior, ResponseCustomHeadersBehavior or ResponseHeadersCorsBehavior to the cloudfront distribution. Passing a custom ResponseSecurityHeadersBehavior is mutually exclusive with turning on the default security headers via ``insertHttpSecurityHeaders`` prop. Will throw an error if both ``insertHttpSecurityHeaders`` is set to ``true`` and ResponseSecurityHeadersBehavior is passed. Default: - undefined

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the CloudFrontToApiGateway class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b39051c9d03e4d1bc82ea6c294d254a848b0b34ee4e5d9d8323f095a78312d0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CloudFrontToApiGatewayProps(
            existing_api_gateway_obj=existing_api_gateway_obj,
            cloud_front_distribution_props=cloud_front_distribution_props,
            cloud_front_logging_bucket_props=cloud_front_logging_bucket_props,
            insert_http_security_headers=insert_http_security_headers,
            response_headers_policy_props=response_headers_policy_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontWebDistribution")
    def cloud_front_web_distribution(
        self,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "cloudFrontWebDistribution"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontFunction")
    def cloud_front_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function], jsii.get(self, "cloudFrontFunction"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontLoggingBucket")
    def cloud_front_logging_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "cloudFrontLoggingBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-cloudfront-apigateway.CloudFrontToApiGatewayProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_api_gateway_obj": "existingApiGatewayObj",
        "cloud_front_distribution_props": "cloudFrontDistributionProps",
        "cloud_front_logging_bucket_props": "cloudFrontLoggingBucketProps",
        "insert_http_security_headers": "insertHttpSecurityHeaders",
        "response_headers_policy_props": "responseHeadersPolicyProps",
    },
)
class CloudFrontToApiGatewayProps:
    def __init__(
        self,
        *,
        existing_api_gateway_obj: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param existing_api_gateway_obj: Existing instance of api.RestApi object. Default: - None
        :param cloud_front_distribution_props: Optional user provided props to override the default props. Default: - Default props are used
        :param cloud_front_logging_bucket_props: Optional user provided props to override the default props for the CloudFront Logging Bucket. Default: - Default props are used
        :param insert_http_security_headers: Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront. Turning this on will inject default headers and is mutually exclusive with passing custom security headers via the responseHeadersPolicyProps parameter. Default: - true
        :param response_headers_policy_props: Optional user provided configuration that cloudfront applies to all http responses. Can be used to pass a custom ResponseSecurityHeadersBehavior, ResponseCustomHeadersBehavior or ResponseHeadersCorsBehavior to the cloudfront distribution. Passing a custom ResponseSecurityHeadersBehavior is mutually exclusive with turning on the default security headers via ``insertHttpSecurityHeaders`` prop. Will throw an error if both ``insertHttpSecurityHeaders`` is set to ``true`` and ResponseSecurityHeadersBehavior is passed. Default: - undefined

        :summary: The properties for the CloudFrontToApiGateway Construct
        '''
        if isinstance(cloud_front_logging_bucket_props, dict):
            cloud_front_logging_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**cloud_front_logging_bucket_props)
        if isinstance(response_headers_policy_props, dict):
            response_headers_policy_props = _aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps(**response_headers_policy_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01cabecaad3c6de210af702ba75eda153a8ba6b2c9c87e9dd7eddf6561f6a8b3)
            check_type(argname="argument existing_api_gateway_obj", value=existing_api_gateway_obj, expected_type=type_hints["existing_api_gateway_obj"])
            check_type(argname="argument cloud_front_distribution_props", value=cloud_front_distribution_props, expected_type=type_hints["cloud_front_distribution_props"])
            check_type(argname="argument cloud_front_logging_bucket_props", value=cloud_front_logging_bucket_props, expected_type=type_hints["cloud_front_logging_bucket_props"])
            check_type(argname="argument insert_http_security_headers", value=insert_http_security_headers, expected_type=type_hints["insert_http_security_headers"])
            check_type(argname="argument response_headers_policy_props", value=response_headers_policy_props, expected_type=type_hints["response_headers_policy_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "existing_api_gateway_obj": existing_api_gateway_obj,
        }
        if cloud_front_distribution_props is not None:
            self._values["cloud_front_distribution_props"] = cloud_front_distribution_props
        if cloud_front_logging_bucket_props is not None:
            self._values["cloud_front_logging_bucket_props"] = cloud_front_logging_bucket_props
        if insert_http_security_headers is not None:
            self._values["insert_http_security_headers"] = insert_http_security_headers
        if response_headers_policy_props is not None:
            self._values["response_headers_policy_props"] = response_headers_policy_props

    @builtins.property
    def existing_api_gateway_obj(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        '''Existing instance of api.RestApi object.

        :default: - None
        '''
        result = self._values.get("existing_api_gateway_obj")
        assert result is not None, "Required property 'existing_api_gateway_obj' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

    @builtins.property
    def cloud_front_distribution_props(self) -> typing.Any:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("cloud_front_distribution_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cloud_front_logging_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''Optional user provided props to override the default props for the CloudFront Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("cloud_front_logging_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def insert_http_security_headers(self) -> typing.Optional[builtins.bool]:
        '''Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront.

        Turning this on will inject default headers and is mutually exclusive with passing custom security headers
        via the responseHeadersPolicyProps parameter.

        :default: - true
        '''
        result = self._values.get("insert_http_security_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def response_headers_policy_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps]:
        '''Optional user provided configuration that cloudfront applies to all http responses.

        Can be used to pass a custom ResponseSecurityHeadersBehavior, ResponseCustomHeadersBehavior or
        ResponseHeadersCorsBehavior to the cloudfront distribution.

        Passing a custom ResponseSecurityHeadersBehavior is mutually exclusive with turning on the default security headers
        via ``insertHttpSecurityHeaders`` prop. Will throw an error if both ``insertHttpSecurityHeaders`` is set to ``true``
        and ResponseSecurityHeadersBehavior is passed.

        :default: - undefined
        '''
        result = self._values.get("response_headers_policy_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFrontToApiGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudFrontToApiGateway",
    "CloudFrontToApiGatewayProps",
]

publication.publish()

def _typecheckingstub__8b39051c9d03e4d1bc82ea6c294d254a848b0b34ee4e5d9d8323f095a78312d0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    existing_api_gateway_obj: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    cloud_front_distribution_props: typing.Any = None,
    cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    insert_http_security_headers: typing.Optional[builtins.bool] = None,
    response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01cabecaad3c6de210af702ba75eda153a8ba6b2c9c87e9dd7eddf6561f6a8b3(
    *,
    existing_api_gateway_obj: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    cloud_front_distribution_props: typing.Any = None,
    cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    insert_http_security_headers: typing.Optional[builtins.bool] = None,
    response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
