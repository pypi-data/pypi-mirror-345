r'''
# aws-openapigateway-lambda module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_openapigateway_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-openapigateway-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.openapigatewaylambda`|

## Overview

This AWS Solutions Construct implements an Amazon API Gateway REST API defined by an OpenAPI specification file connected to an AWS Lambda function.

Here is a minimal deployable pattern definition.

**NOTE** The referenced `openapi/apiDefinition.yaml` openapi definition file and `messages-lambda` lambda package directory for the three code samples below can both be found under this constructs `test` folder (`<repository_root>/source/patterns/@aws-solutions-constructs/aws-openapigateway-lambda/test`)

Typescript

```python
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { OpenApiGatewayToLambda } from '@aws-solutions-constructs/aws-openapigateway-lambda';
import { Asset } from 'aws-cdk-lib/aws-s3-assets';
import * as path from 'path';
import * as lambda from 'aws-cdk-lib/aws-lambda';

const apiDefinitionAsset = new Asset(this, 'ApiDefinitionAsset', {
  path: path.join(__dirname, 'openapi/apiDefinition.yaml')
});

new OpenApiGatewayToLambda(this, 'OpenApiGatewayToLambda', {
  apiDefinitionAsset,
  apiIntegrations: [
    {
      id: 'MessagesHandler',
      lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_20_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`${__dirname}/messages-lambda`),
      }
    }
  ]
});
```

Python

```python
from aws_cdk import (
    Stack,
    aws_s3_assets as s3_assets,
    aws_lambda as lambda_,
)
from constructs import Construct
from aws_solutions_constructs.aws_openapigateway_lambda import OpenApiGatewayToLambda, ApiIntegration

class TestStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api_definition_asset = s3_assets.Asset(self, "ApiDefinitionAsset", path="./openapi/apiDefinition.yaml")

        api_integration = ApiIntegration(id="MessagesHandler", lambda_function_props={
            "runtime": lambda_.Runtime.NODEJS_20_X,
            "handler": "index.handler",
            "code": lambda_.Code.from_asset("./messages-lambda")
        })

        openapigateway_to_lambda = OpenApiGatewayToLambda(self,
            id="OpenApiGatewayToLambda",
            api_integrations=[api_integration],
            api_definition_asset=api_definition_asset
        )
```

Java

```java
import software.amazon.awscdk.services.lambda.Code;
import software.amazon.awscdk.services.lambda.FunctionProps;
import software.amazon.awscdk.services.s3.assets.Asset;
import software.amazon.awscdk.services.s3.assets.AssetProps;
import software.amazon.awsconstructs.services.openapigatewaylambda.ApiIntegration;
import software.amazon.awsconstructs.services.openapigatewaylambda.OpenApiGatewayToLambda;
import software.amazon.awsconstructs.services.openapigatewaylambda.OpenApiGatewayToLambdaProps;
import software.constructs.Construct;
import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;

import java.util.Collections;

import static software.amazon.awscdk.services.lambda.Runtime.NODEJS_20_X;

final Asset apiDefinitionAsset = new Asset(this, "ApiDefinition", AssetProps.builder().path("openapi/apiDefinition.yaml").build());

final ApiIntegration apiIntegration = ApiIntegration.builder()
    .id("MessagesHandler")
    .lambdaFunctionProps(new FunctionProps.Builder()
        .runtime(NODEJS_20_X)
        .code(Code.fromAsset("messages-lambda"))
        .handler("index.handler")
        .build())
    .build();

new OpenApiGatewayToLambda(this, "OpenApiGatewayToLambda", OpenApiGatewayToLambdaProps.builder()
    .apiDefinitionAsset(apiDefinitionAsset)
    .apiIntegrations(Collections.singletonList(apiIntegration))
    .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGatewayProps?|[`apigateway.RestApiBaseProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.RestApiBaseProps.html)|Optional user-provided props to override the default props for the API.|
|apiDefinitionBucket?|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.IBucket.html)|S3 Bucket where the OpenAPI spec file is located. When specifying this property, `apiDefinitionKey` must also be specified.|
|apiDefinitionKey?|`string`|S3 Object name of the OpenAPI spec file. When specifying this property, `apiDefinitionBucket` must also be specified.|
|apiDefinitionAsset?|[`aws_s3_assets.Asset`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3_assets.Asset.html)|Local file asset of the OpenAPI spec file.|
|apiDefinitionJson?|any|OpenAPI specification represented in a JSON object to be embedded in the CloudFormation template. IMPORTANT - Including the spec in the template introduces a risk of the template growing too big, but there are some use cases that require an embedded spec. Unless your use case explicitly requires an embedded spec you should pass your spec as an S3 asset.|
|apiIntegrations|`ApiIntegration[]`|One or more key-value pairs that contain an id for the api integration and either an existing lambda function or an instance of the LambdaProps. Please see the `Overview of how the OpenAPI file transformation works` section below for more usage details.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiLambdaFunctions|`ApiLambdaFunction[]`|Returns an array of ApiLambdaFunction objects, where each has an `id` of the `apiIntegration` and the corresponding `lambda.Function` that it maps to.|
|apiGateway|[`api.SpecRestApi`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.SpecRestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|

## Interfaces defined by this construct

`ApiIntegration`
Maps a Lambda function to the id string used as a placeholder in the OpenAPI spec. The type has a required property, `id`, and two optional properties `existingLambdaObj`, and `lambdaFunctionProps`. The `id` property is used to map the corresponding lambda function being defined with the placeholder string in the OpenAPI template file, and is not a CDK construct ID. Exactly one of `existingLambdaObj` or `lambdaFunctionProps` must be specified or the construct will throw an error. The `existingLambaObj` property will accept a lambda.Function object OR a lambda.Alias object. The property `ApiIntegrations` is an array of this interface and is a required property when launching this construct.

`ApiLambdaFunction`
This interface returns the Lambda objects used when launching the construct. The `id` property will always be set, if an existing function was provided in the props or this construct created a new Lambda function, then that function will be in the `lambdaFunction` property. If a Lambda Alias was provided in the props, then that value will be specified in the `functionAlias` property. At no time will `lambdaFunction` and `functionAlias` be set on the same ApiLambdaFunction object. The construct exposes an array of these objects as a property.

## Overview of how the OpenAPI file transformation works

This construct automatically transforms an incoming OpenAPI Definition (residing locally or in S3) by auto-populating the `uri` fields of the `x-amazon-apigateway-integration` integrations with the resolved value of the backing lambda functions. It does so by allowing the user to specify the `apiIntegrations` property and then correlates it with the api definition.

Looking at an example - a user creates an instantiation of `apiIntegrations` that specifies one integration named `MessagesHandler` that passes in a set of `lambda.FunctionProps` and a second integration named `PhotosHandler` that passes in an existing `lambda.Function`:

```python
const apiIntegrations: ApiIntegration[] = [
  {
    id: 'MessagesHandler',
    lambdaFunctionProps: {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(`${__dirname}/messages-lambda`),
    }
  },
  {
    id: 'PhotosHandler',
    existingLambdaObj: new lambda.Function(this, 'PhotosLambda', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(`${__dirname}/photos-lambda`),
    })
  }
]
```

And a corresponding api definition with `GET` and `POST` methods on a `/messages` resource and a `GET` method on a `/photos` resource.

```
openapi: "3.0.1"
info:
  title: "api"
  version: "2023-02-20T20:46:08Z"
paths:
  /messages:
    get:
      x-amazon-apigateway-integration:
        httpMethod: "POST"
        uri: MessagesHandler
        passthroughBehavior: "when_no_match"
        type: "aws_proxy"
    post:
      x-amazon-apigateway-integration:
        httpMethod: "POST"
        uri: MessagesHandler
        passthroughBehavior: "when_no_match"
        type: "aws_proxy"
  /photos:
    get:
      x-amazon-apigateway-integration:
        httpMethod: "POST"
        uri: PhotosHandler
        passthroughBehavior: "when_no_match"
        type: "aws_proxy"
```

When the construct is created or updated, it will overwrite the `MessagesHandler` string with the fully resolved lambda proxy uri of the `MessagesHandlerLambdaFunction`, e.g., `arn:${Aws.PARTITION}:apigateway:${Aws.REGION}:lambda:path/2015-03-31/functions/${messagesLambda.functionArn}/invocations`, and similarly for the `PhotosHandler` string and `PhotosHandlerLambdaFunction`, resulting in a valid OpenAPI spec file that is then passed to the `SpecRestApi` construct.

For more information on specifying an API with OpenAPI, please see the [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon API Gateway

* Deploy an edge-optimized API endpoint
* Enable CloudWatch logging for API Gateway
* Configure least privilege access IAM role for API Gateway
* Enable X-Ray Tracing

### AWS Lambda Function

* Configure limited privilege access IAM roles for Lambda functions
* Enable reusing connections with Keep-Alive for NodeJs Lambda functions
* Enable X-Ray Tracing
* Set Environment Variables

  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-openapigateway-lambda.ApiIntegration",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "existing_lambda_obj": "existingLambdaObj",
        "lambda_function_props": "lambdaFunctionProps",
    },
)
class ApiIntegration:
    def __init__(
        self,
        *,
        id: builtins.str,
        existing_lambda_obj: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.Function, _aws_cdk_aws_lambda_ceddda9d.Alias]] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''The ApiIntegration interface is used to correlate a user-specified id with either a existing lambda function or set of lambda props.

        See the 'Overview of how the OpenAPI file transformation works' section of the README.md for more details on its usage.

        :param id: Id of the ApiIntegration, used to correlate this lambda function to the api integration in the open api definition. Note this is not a CDK Construct ID, and is instead a client defined string used to map the resolved lambda resource with the OpenAPI definition.
        :param existing_lambda_obj: The Lambda function to associate with the API method in the OpenAPI file matched by id. One and only one of existingLambdaObj or lambdaFunctionProps must be specified, any other combination will cause an error.
        :param lambda_function_props: Properties for the Lambda function to create and associate with the API method in the OpenAPI file matched by id. One and only one of existingLambdaObj or lambdaFunctionProps must be specified, any other combination will cause an error.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b1a09e9bbf57f6b9c31a7e98f3c22bf1f14ee32a481f88b7c6a5dae44c51063)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props

    @builtins.property
    def id(self) -> builtins.str:
        '''Id of the ApiIntegration, used to correlate this lambda function to the api integration in the open api definition.

        Note this is not a CDK Construct ID, and is instead a client defined string used to map the resolved lambda resource with the OpenAPI definition.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def existing_lambda_obj(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.Function, _aws_cdk_aws_lambda_ceddda9d.Alias]]:
        '''The Lambda function to associate with the API method in the OpenAPI file matched by id.

        One and only one of existingLambdaObj or lambdaFunctionProps must be specified, any other combination will cause an error.
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.Function, _aws_cdk_aws_lambda_ceddda9d.Alias]], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''Properties for the Lambda function to create and associate with the API method in the OpenAPI file matched by id.

        One and only one of existingLambdaObj or lambdaFunctionProps must be specified, any other combination will cause an error.
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiIntegration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-openapigateway-lambda.ApiLambdaFunction",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "function_alias": "functionAlias",
        "lambda_function": "lambdaFunction",
    },
)
class ApiLambdaFunction:
    def __init__(
        self,
        *,
        id: builtins.str,
        function_alias: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Alias] = None,
        lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    ) -> None:
        '''Helper object to map an ApiIntegration id to its resolved lambda.Function. This type is exposed as a property on the instantiated construct.

        :param id: Id of the ApiIntegration, used to correlate this lambda function to the api integration in the open api definition.
        :param function_alias: -
        :param lambda_function: The function the API method will integrate with - Must be defined in lambdaFunction or functionAlias (but not both).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b34df00db45a414bf2a2dd0aa85c226040b27bc33e6b02e652a7c94c036c86c)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument function_alias", value=function_alias, expected_type=type_hints["function_alias"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if function_alias is not None:
            self._values["function_alias"] = function_alias
        if lambda_function is not None:
            self._values["lambda_function"] = lambda_function

    @builtins.property
    def id(self) -> builtins.str:
        '''Id of the ApiIntegration, used to correlate this lambda function to the api integration in the open api definition.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_alias(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Alias]:
        result = self._values.get("function_alias")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Alias], result)

    @builtins.property
    def lambda_function(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''The function the API method will integrate with - Must be defined in lambdaFunction or functionAlias (but not both).'''
        result = self._values.get("lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiLambdaFunction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenApiGatewayToLambda(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-openapigateway-lambda.OpenApiGatewayToLambda",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_integrations: typing.Sequence[typing.Union[ApiIntegration, typing.Dict[builtins.str, typing.Any]]],
        api_definition_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        api_definition_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        api_definition_json: typing.Any = None,
        api_definition_key: typing.Optional[builtins.str] = None,
        api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
        internal_transform_memory_size: typing.Optional[jsii.Number] = None,
        internal_transform_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_integrations: One or more key-value pairs that contain an id for the api integration and either an existing lambda function or an instance of the LambdaProps. Example: const apiIntegrations: ApiIntegration[] = [ { id: 'MessagesHandler', lambdaFunctionProps: { runtime: defaults.COMMERCIAL_REGION_LAMBDA_NODE_RUNTIME, handler: 'index.handler', code: lambda.Code.fromAsset(``${__dirname}/messages-lambda``), } }, { id: 'PhotosHandler', existingLambdaObj: new lambda.Function(this, 'PhotosLambda', { runtime: defaults.COMMERCIAL_REGION_LAMBDA_NODE_RUNTIME, handler: 'index.handler', code: lambda.Code.fromAsset(``${__dirname}/photos-lambda``), }) } ]
        :param api_definition_asset: Local file asset of the OpenAPI spec file.
        :param api_definition_bucket: S3 Bucket where the OpenAPI spec file is located. When specifying this property, apiDefinitionKey must also be specified.
        :param api_definition_json: OpenAPI specification represented in a JSON object to be embedded in the CloudFormation template. IMPORTANT - Including the spec in the template introduces a risk of the template growing too big, but there are some use cases that require an embedded spec. Unless your use case explicitly requires an embedded spec you should pass your spec as an S3 asset.
        :param api_definition_key: S3 Object name of the OpenAPI spec file. When specifying this property, apiDefinitionBucket must also be specified.
        :param api_gateway_props: Optional user-provided props to override the default props for the API. Default: - Default props are used.
        :param internal_transform_memory_size: Optional user-defined memory size for the Lambda function custom resource installed to do the OpenAPI definition transformation. This setting does not affect the deployed architecture - only the ability for the Construct to complete its work. Defaults to 1024 MiB, but for larger files (hundreds of megabytes or gigabytes in size) this value may need to be increased. Default: 1024
        :param internal_transform_timeout: Optional user-defined timeout for the Lambda function custom resource installed to do the OpenAPI definition transformation. This setting does not affect the deployed architecture - only the ability for the Construct to complete its work. Defaults to 1 minute, but for larger files (hundreds of megabytes or gigabytes in size) this value may need to be increased. Default: Duration.minutes(1)
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f72b11c0dbf5d67e28186e991bb77d43c6063fb3d69758a2d112ff6a531924e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenApiGatewayToLambdaProps(
            api_integrations=api_integrations,
            api_definition_asset=api_definition_asset,
            api_definition_bucket=api_definition_bucket,
            api_definition_json=api_definition_json,
            api_definition_key=api_definition_key,
            api_gateway_props=api_gateway_props,
            internal_transform_memory_size=internal_transform_memory_size,
            internal_transform_timeout=internal_transform_timeout,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.SpecRestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="apiLambdaFunctions")
    def api_lambda_functions(self) -> typing.List[ApiLambdaFunction]:
        return typing.cast(typing.List[ApiLambdaFunction], jsii.get(self, "apiLambdaFunctions"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-openapigateway-lambda.OpenApiGatewayToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_integrations": "apiIntegrations",
        "api_definition_asset": "apiDefinitionAsset",
        "api_definition_bucket": "apiDefinitionBucket",
        "api_definition_json": "apiDefinitionJson",
        "api_definition_key": "apiDefinitionKey",
        "api_gateway_props": "apiGatewayProps",
        "internal_transform_memory_size": "internalTransformMemorySize",
        "internal_transform_timeout": "internalTransformTimeout",
        "log_group_props": "logGroupProps",
    },
)
class OpenApiGatewayToLambdaProps:
    def __init__(
        self,
        *,
        api_integrations: typing.Sequence[typing.Union[ApiIntegration, typing.Dict[builtins.str, typing.Any]]],
        api_definition_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        api_definition_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        api_definition_json: typing.Any = None,
        api_definition_key: typing.Optional[builtins.str] = None,
        api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
        internal_transform_memory_size: typing.Optional[jsii.Number] = None,
        internal_transform_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_integrations: One or more key-value pairs that contain an id for the api integration and either an existing lambda function or an instance of the LambdaProps. Example: const apiIntegrations: ApiIntegration[] = [ { id: 'MessagesHandler', lambdaFunctionProps: { runtime: defaults.COMMERCIAL_REGION_LAMBDA_NODE_RUNTIME, handler: 'index.handler', code: lambda.Code.fromAsset(``${__dirname}/messages-lambda``), } }, { id: 'PhotosHandler', existingLambdaObj: new lambda.Function(this, 'PhotosLambda', { runtime: defaults.COMMERCIAL_REGION_LAMBDA_NODE_RUNTIME, handler: 'index.handler', code: lambda.Code.fromAsset(``${__dirname}/photos-lambda``), }) } ]
        :param api_definition_asset: Local file asset of the OpenAPI spec file.
        :param api_definition_bucket: S3 Bucket where the OpenAPI spec file is located. When specifying this property, apiDefinitionKey must also be specified.
        :param api_definition_json: OpenAPI specification represented in a JSON object to be embedded in the CloudFormation template. IMPORTANT - Including the spec in the template introduces a risk of the template growing too big, but there are some use cases that require an embedded spec. Unless your use case explicitly requires an embedded spec you should pass your spec as an S3 asset.
        :param api_definition_key: S3 Object name of the OpenAPI spec file. When specifying this property, apiDefinitionBucket must also be specified.
        :param api_gateway_props: Optional user-provided props to override the default props for the API. Default: - Default props are used.
        :param internal_transform_memory_size: Optional user-defined memory size for the Lambda function custom resource installed to do the OpenAPI definition transformation. This setting does not affect the deployed architecture - only the ability for the Construct to complete its work. Defaults to 1024 MiB, but for larger files (hundreds of megabytes or gigabytes in size) this value may need to be increased. Default: 1024
        :param internal_transform_timeout: Optional user-defined timeout for the Lambda function custom resource installed to do the OpenAPI definition transformation. This setting does not affect the deployed architecture - only the ability for the Construct to complete its work. Defaults to 1 minute, but for larger files (hundreds of megabytes or gigabytes in size) this value may need to be increased. Default: Duration.minutes(1)
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        '''
        if isinstance(api_gateway_props, dict):
            api_gateway_props = _aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps(**api_gateway_props)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf1c5fb01583839f606ad44a970067741d586951b8ec3e6b0a23aa04684efd0)
            check_type(argname="argument api_integrations", value=api_integrations, expected_type=type_hints["api_integrations"])
            check_type(argname="argument api_definition_asset", value=api_definition_asset, expected_type=type_hints["api_definition_asset"])
            check_type(argname="argument api_definition_bucket", value=api_definition_bucket, expected_type=type_hints["api_definition_bucket"])
            check_type(argname="argument api_definition_json", value=api_definition_json, expected_type=type_hints["api_definition_json"])
            check_type(argname="argument api_definition_key", value=api_definition_key, expected_type=type_hints["api_definition_key"])
            check_type(argname="argument api_gateway_props", value=api_gateway_props, expected_type=type_hints["api_gateway_props"])
            check_type(argname="argument internal_transform_memory_size", value=internal_transform_memory_size, expected_type=type_hints["internal_transform_memory_size"])
            check_type(argname="argument internal_transform_timeout", value=internal_transform_timeout, expected_type=type_hints["internal_transform_timeout"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_integrations": api_integrations,
        }
        if api_definition_asset is not None:
            self._values["api_definition_asset"] = api_definition_asset
        if api_definition_bucket is not None:
            self._values["api_definition_bucket"] = api_definition_bucket
        if api_definition_json is not None:
            self._values["api_definition_json"] = api_definition_json
        if api_definition_key is not None:
            self._values["api_definition_key"] = api_definition_key
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if internal_transform_memory_size is not None:
            self._values["internal_transform_memory_size"] = internal_transform_memory_size
        if internal_transform_timeout is not None:
            self._values["internal_transform_timeout"] = internal_transform_timeout
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def api_integrations(self) -> typing.List[ApiIntegration]:
        '''One or more key-value pairs that contain an id for the api integration and either an existing lambda function or an instance of the LambdaProps.

        Example:
        const apiIntegrations: ApiIntegration[] = [
        {
        id: 'MessagesHandler',
        lambdaFunctionProps: {
        runtime: defaults.COMMERCIAL_REGION_LAMBDA_NODE_RUNTIME,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(``${__dirname}/messages-lambda``),
        }
        },
        {
        id: 'PhotosHandler',
        existingLambdaObj: new lambda.Function(this, 'PhotosLambda', {
        runtime: defaults.COMMERCIAL_REGION_LAMBDA_NODE_RUNTIME,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(``${__dirname}/photos-lambda``),
        })
        }
        ]
        '''
        result = self._values.get("api_integrations")
        assert result is not None, "Required property 'api_integrations' is missing"
        return typing.cast(typing.List[ApiIntegration], result)

    @builtins.property
    def api_definition_asset(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''Local file asset of the OpenAPI spec file.'''
        result = self._values.get("api_definition_asset")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], result)

    @builtins.property
    def api_definition_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''S3 Bucket where the OpenAPI spec file is located.

        When specifying this property, apiDefinitionKey must also be specified.
        '''
        result = self._values.get("api_definition_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def api_definition_json(self) -> typing.Any:
        '''OpenAPI specification represented in a JSON object to be embedded in the CloudFormation template.

        IMPORTANT - Including the spec in the template introduces a risk of the template growing too big, but
        there are some use cases that require an embedded spec. Unless your use case explicitly requires an embedded spec
        you should pass your spec as an S3 asset.
        '''
        result = self._values.get("api_definition_json")
        return typing.cast(typing.Any, result)

    @builtins.property
    def api_definition_key(self) -> typing.Optional[builtins.str]:
        '''S3 Object name of the OpenAPI spec file.

        When specifying this property, apiDefinitionBucket must also be specified.
        '''
        result = self._values.get("api_definition_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_gateway_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps]:
        '''Optional user-provided props to override the default props for the API.

        :default: - Default props are used.
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps], result)

    @builtins.property
    def internal_transform_memory_size(self) -> typing.Optional[jsii.Number]:
        '''Optional user-defined memory size for the Lambda function custom resource installed to do the OpenAPI definition transformation.

        This setting does not affect the deployed architecture - only the ability for the Construct to complete its work.

        Defaults to 1024 MiB, but for larger files (hundreds of megabytes or gigabytes in size) this value may need to be increased.

        :default: 1024
        '''
        result = self._values.get("internal_transform_memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def internal_transform_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Optional user-defined timeout for the Lambda function custom resource installed to do the OpenAPI definition transformation.

        This setting does not affect the deployed architecture - only the ability for the Construct to complete its work.

        Defaults to 1 minute, but for larger files (hundreds of megabytes or gigabytes in size) this value may need to be increased.

        :default: Duration.minutes(1)
        '''
        result = self._values.get("internal_transform_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

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
        return "OpenApiGatewayToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiIntegration",
    "ApiLambdaFunction",
    "OpenApiGatewayToLambda",
    "OpenApiGatewayToLambdaProps",
]

publication.publish()

def _typecheckingstub__9b1a09e9bbf57f6b9c31a7e98f3c22bf1f14ee32a481f88b7c6a5dae44c51063(
    *,
    id: builtins.str,
    existing_lambda_obj: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.Function, _aws_cdk_aws_lambda_ceddda9d.Alias]] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b34df00db45a414bf2a2dd0aa85c226040b27bc33e6b02e652a7c94c036c86c(
    *,
    id: builtins.str,
    function_alias: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Alias] = None,
    lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f72b11c0dbf5d67e28186e991bb77d43c6063fb3d69758a2d112ff6a531924e0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_integrations: typing.Sequence[typing.Union[ApiIntegration, typing.Dict[builtins.str, typing.Any]]],
    api_definition_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    api_definition_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    api_definition_json: typing.Any = None,
    api_definition_key: typing.Optional[builtins.str] = None,
    api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
    internal_transform_memory_size: typing.Optional[jsii.Number] = None,
    internal_transform_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf1c5fb01583839f606ad44a970067741d586951b8ec3e6b0a23aa04684efd0(
    *,
    api_integrations: typing.Sequence[typing.Union[ApiIntegration, typing.Dict[builtins.str, typing.Any]]],
    api_definition_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    api_definition_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    api_definition_json: typing.Any = None,
    api_definition_key: typing.Optional[builtins.str] = None,
    api_gateway_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
    internal_transform_memory_size: typing.Optional[jsii.Number] = None,
    internal_transform_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
