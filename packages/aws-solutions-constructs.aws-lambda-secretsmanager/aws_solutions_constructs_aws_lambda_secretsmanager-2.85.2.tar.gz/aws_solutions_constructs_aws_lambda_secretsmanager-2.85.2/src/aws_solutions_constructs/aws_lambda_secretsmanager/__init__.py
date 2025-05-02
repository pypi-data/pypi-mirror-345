r'''
# aws-lambda-secretsmanager module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_secretsmanager`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-secretsmanager`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdasecretsmanager`|

## Overview

This AWS Solutions Construct implements the AWS Lambda function and AWS Secrets Manager secret with the least privileged permissions.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { LambdaToSecretsmanagerProps, LambdaToSecretsmanager } from '@aws-solutions-constructs/aws-lambda-secretsmanager';
import * as lambda from 'aws-cdk-lib/aws-lambda';

const constructProps: LambdaToSecretsmanagerProps = {
  lambdaFunctionProps: {
    runtime: lambda.Runtime.NODEJS_20_X,
    code: lambda.Code.fromAsset(`lambda`),
    handler: 'index.handler'
  },
};

new LambdaToSecretsmanager(this, 'test-lambda-secretsmanager-stack', constructProps);
```

Python

```python
from aws_solutions_constructs.aws_lambda_secretsmanager import LambdaToSecretsmanagerProps, LambdaToSecretsmanager
from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)
from constructs import Construct


LambdaToSecretsmanager(
    self, 'test-lambda-secretsmanager-stack',
    lambda_function_props=_lambda.FunctionProps(
        code=_lambda.Code.from_asset('lambda'),
        runtime=_lambda.Runtime.PYTHON_3_11,
        handler='index.handler'
    )
)
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.services.lambda.*;
import software.amazon.awscdk.services.lambda.Runtime;
import software.amazon.awsconstructs.services.lambdasecretsmanager.*;

new LambdaToSecretsmanager(this, "test-lambda-secretsmanager-stack", new LambdaToSecretsmanagerProps.Builder()
        .lambdaFunctionProps(new FunctionProps.Builder()
                .runtime(Runtime.NODEJS_20_X)
                .code(Code.fromAsset("lambda"))
                .handler("index.handler")
                .build())
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|secretProps?|[`secretsmanager.SecretProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_secretsmanager.SecretProps.html)|Optional user provided props to override the default props for Secrets Manager|
|existingSecretObj?|[`secretsmanager.Secret`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_secretsmanager.Secret.html)|Existing instance of Secrets Manager Secret object, If this is set then the secretProps is ignored|
|grantWriteAccess?|`string`|Optional Access granted to the Lambda function for the secret. 'Read' or 'ReadWrite". Default is "Read"
|secretEnvironmentVariableName?|`string`|Optional Name for the Lambda function environment variable set to the ARN of the secret. Default: SECRET_ARN. |
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for AWS Secrets Manager. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overridden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html)|Returns an instance of lambda.Function created by the construct|
|secret|[`secretsmanager.Secret`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_secretsmanager.Secret.html)|Returns an instance of secretsmanager.Secret created by the construct|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * (default) SECRET_ARN containing the ARN of the secret as return by CDK [secretArn property](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_secretsmanager.Secret.html#secretarn).
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon SecretsManager Secret

* Enable read-only access for the associated AWS Lambda Function
* Creates a new Secret

  * (default) random name
  * (default) random value
* Retain the Secret when deleting the CloudFormation stack

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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


class LambdaToSecretsmanager(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-secretsmanager.LambdaToSecretsmanager",
):
    '''
    :summary: The LambdaToSecretsmanager class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_secret_obj: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        grant_write_access: typing.Optional[builtins.str] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        secret_environment_variable_name: typing.Optional[builtins.str] = None,
        secret_props: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_secret_obj: Existing instance of Secret object, providing both this and secretProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param grant_write_access: Optional secret permissions to grant to the Lambda function. One of the following may be specified: "Read" or "ReadWrite". Default: - Read only access is given to the Lambda function if no value is specified.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param secret_environment_variable_name: Optional Name for the Lambda function environment variable set to the ARN of the secret. Default: - SECRET_ARN
        :param secret_props: Optional user-provided props to override the default props for the Secret. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :summary: Constructs a new instance of the LambdaToSecretsmanager class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__444fb83809c5da8f4e91f86156cafd25a7ec722f3c37e439ea9d205271b23b12)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LambdaToSecretsmanagerProps(
            deploy_vpc=deploy_vpc,
            existing_lambda_obj=existing_lambda_obj,
            existing_secret_obj=existing_secret_obj,
            existing_vpc=existing_vpc,
            grant_write_access=grant_write_access,
            lambda_function_props=lambda_function_props,
            secret_environment_variable_name=secret_environment_variable_name,
            secret_props=secret_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.Secret:
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.Secret, jsii.get(self, "secret"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-secretsmanager.LambdaToSecretsmanagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_vpc": "deployVpc",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_secret_obj": "existingSecretObj",
        "existing_vpc": "existingVpc",
        "grant_write_access": "grantWriteAccess",
        "lambda_function_props": "lambdaFunctionProps",
        "secret_environment_variable_name": "secretEnvironmentVariableName",
        "secret_props": "secretProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToSecretsmanagerProps:
    def __init__(
        self,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_secret_obj: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        grant_write_access: typing.Optional[builtins.str] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        secret_environment_variable_name: typing.Optional[builtins.str] = None,
        secret_props: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_secret_obj: Existing instance of Secret object, providing both this and secretProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param grant_write_access: Optional secret permissions to grant to the Lambda function. One of the following may be specified: "Read" or "ReadWrite". Default: - Read only access is given to the Lambda function if no value is specified.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param secret_environment_variable_name: Optional Name for the Lambda function environment variable set to the ARN of the secret. Default: - SECRET_ARN
        :param secret_props: Optional user-provided props to override the default props for the Secret. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToSecretsmanager class.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(secret_props, dict):
            secret_props = _aws_cdk_aws_secretsmanager_ceddda9d.SecretProps(**secret_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df69763c9616cce5c96cc24ad89f9f2342ec78081d7504421770c379d70520d0)
            check_type(argname="argument deploy_vpc", value=deploy_vpc, expected_type=type_hints["deploy_vpc"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument existing_secret_obj", value=existing_secret_obj, expected_type=type_hints["existing_secret_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument grant_write_access", value=grant_write_access, expected_type=type_hints["grant_write_access"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument secret_environment_variable_name", value=secret_environment_variable_name, expected_type=type_hints["secret_environment_variable_name"])
            check_type(argname="argument secret_props", value=secret_props, expected_type=type_hints["secret_props"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_secret_obj is not None:
            self._values["existing_secret_obj"] = existing_secret_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if grant_write_access is not None:
            self._values["grant_write_access"] = grant_write_access
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if secret_environment_variable_name is not None:
            self._values["secret_environment_variable_name"] = secret_environment_variable_name
        if secret_props is not None:
            self._values["secret_props"] = secret_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def deploy_vpc(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a new VPC.

        :default: - false
        '''
        result = self._values.get("deploy_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_lambda_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def existing_secret_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret]:
        '''Existing instance of Secret object, providing both this and secretProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_secret_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def grant_write_access(self) -> typing.Optional[builtins.str]:
        '''Optional secret permissions to grant to the Lambda function.

        One of the following may be specified: "Read" or "ReadWrite".

        :default: - Read only access is given to the Lambda function if no value is specified.
        '''
        result = self._values.get("grant_write_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    @builtins.property
    def secret_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the ARN of the secret.

        :default: - SECRET_ARN
        '''
        result = self._values.get("secret_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps]:
        '''Optional user-provided props to override the default props for the Secret.

        :default: - Default props are used
        '''
        result = self._values.get("secret_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''Properties to override default properties if deployVpc is true.'''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToSecretsmanagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToSecretsmanager",
    "LambdaToSecretsmanagerProps",
]

publication.publish()

def _typecheckingstub__444fb83809c5da8f4e91f86156cafd25a7ec722f3c37e439ea9d205271b23b12(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_secret_obj: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    grant_write_access: typing.Optional[builtins.str] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    secret_environment_variable_name: typing.Optional[builtins.str] = None,
    secret_props: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df69763c9616cce5c96cc24ad89f9f2342ec78081d7504421770c379d70520d0(
    *,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_secret_obj: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    grant_write_access: typing.Optional[builtins.str] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    secret_environment_variable_name: typing.Optional[builtins.str] = None,
    secret_props: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
