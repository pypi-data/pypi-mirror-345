r'''
# aws-lambda-dynamodb module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_dynamodb`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-dynamodb`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdadynamodb`|

## Overview

This AWS Solutions Construct implements the AWS Lambda function and Amazon DynamoDB table with the least privileged permissions.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { LambdaToDynamoDBProps, LambdaToDynamoDB } from '@aws-solutions-constructs/aws-lambda-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';

const constructProps: LambdaToDynamoDBProps = {
  lambdaFunctionProps: {
    code: lambda.Code.fromAsset(`lambda`),
    runtime: lambda.Runtime.NODEJS_20_X,
    handler: 'index.handler'
  },
};

new LambdaToDynamoDB(this, 'test-lambda-dynamodb-stack', constructProps);
```

Python

```python
from aws_solutions_constructs.aws_lambda_dynamodb import LambdaToDynamoDBProps, LambdaToDynamoDB
from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)
from constructs import Construct

LambdaToDynamoDB(self, 'test_lambda_dynamodb_stack',
                    lambda_function_props=_lambda.FunctionProps(
                        code=_lambda.Code.from_asset(
                            'lambda'),
                        runtime=_lambda.Runtime.PYTHON_3_11,
                        handler='index.handler'
                    ))
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.services.lambda.*;
import software.amazon.awscdk.services.lambda.Runtime;
import software.amazon.awsconstructs.services.lambdadynamodb.*;

new LambdaToDynamoDB(this, "test_lambda_dynamodb_stack", new LambdaToDynamoDBProps.Builder()
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
|dynamoTableProps?|[`dynamodb.TableProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_dynamodb.TableProps.html)|Optional user provided props to override the default props for DynamoDB Table|
|existingTableObj?|[`dynamodb.Table`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_dynamodb.Table.html)|Existing instance of DynamoDB table object, providing both this and `dynamoTableProps` will cause an error.|
|tablePermissions?|`string`|Optional table permissions to grant to the Lambda function. One of the following may be specified: `All`, `Read`, `ReadWrite`, `Write`.|
|tableEnvironmentVariableName?|`string`|Optional Name for the Lambda function environment variable set to the name of the DynamoDB table. Default: DDB_TABLE_NAME |
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and a Gateway Endpoint will be created in the VPC for Amazon DynamoDB. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overridden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html)|Returns an instance of lambda.Function created by the construct|
|dynamoTable|[`dynamodb.Table`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_dynamodb.Table.html)|Returns an instance of dynamodb.Table created by the construct|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * (default) DDB_TABLE_NAME
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon DynamoDB Table

* Set the billing mode for DynamoDB Table to On-Demand (Pay per request)
* Enable server-side encryption for DynamoDB Table using AWS managed KMS Key
* Creates a partition key called 'id' for DynamoDB Table
* Retain the Table when deleting the CloudFormation stack
* Enable continuous backups and point-in-time recovery

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

import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import constructs as _constructs_77d1e7e8


class LambdaToDynamoDB(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-dynamodb.LambdaToDynamoDB",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        table_environment_variable_name: typing.Optional[builtins.str] = None,
        table_permissions: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_table_obj: Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param table_environment_variable_name: Optional Name for the Lambda function environment variable set to the name of the DynamoDB table. Default: - DDB_TABLE_NAME
        :param table_permissions: Optional table permissions to grant to the Lambda function. One of the following may be specified: "All", "Read", "ReadWrite", "Write". Default: - Read/write access is given to the Lambda function if no value is specified.
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the LambdaToDynamoDB class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__092571f3790131920e423b6b48f6ada271812c0ab4c4b76127eec81553b7a3b0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LambdaToDynamoDBProps(
            deploy_vpc=deploy_vpc,
            dynamo_table_props=dynamo_table_props,
            existing_lambda_obj=existing_lambda_obj,
            existing_table_obj=existing_table_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            table_environment_variable_name=table_environment_variable_name,
            table_permissions=table_permissions,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="dynamoTable")
    def dynamo_table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "dynamoTable"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-dynamodb.LambdaToDynamoDBProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_vpc": "deployVpc",
        "dynamo_table_props": "dynamoTableProps",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_table_obj": "existingTableObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "table_environment_variable_name": "tableEnvironmentVariableName",
        "table_permissions": "tablePermissions",
        "vpc_props": "vpcProps",
    },
)
class LambdaToDynamoDBProps:
    def __init__(
        self,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        table_environment_variable_name: typing.Optional[builtins.str] = None,
        table_permissions: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_table_obj: Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param table_environment_variable_name: Optional Name for the Lambda function environment variable set to the name of the DynamoDB table. Default: - DDB_TABLE_NAME
        :param table_permissions: Optional table permissions to grant to the Lambda function. One of the following may be specified: "All", "Read", "ReadWrite", "Write". Default: - Read/write access is given to the Lambda function if no value is specified.
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToDynamoDB Construct
        '''
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = _aws_cdk_aws_dynamodb_ceddda9d.TableProps(**dynamo_table_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c30a6a57824df9f62e5321acb93af2c3fb40432124ad8139a8da216f3d87fc)
            check_type(argname="argument deploy_vpc", value=deploy_vpc, expected_type=type_hints["deploy_vpc"])
            check_type(argname="argument dynamo_table_props", value=dynamo_table_props, expected_type=type_hints["dynamo_table_props"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument existing_table_obj", value=existing_table_obj, expected_type=type_hints["existing_table_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument table_environment_variable_name", value=table_environment_variable_name, expected_type=type_hints["table_environment_variable_name"])
            check_type(argname="argument table_permissions", value=table_permissions, expected_type=type_hints["table_permissions"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_table_obj is not None:
            self._values["existing_table_obj"] = existing_table_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if table_environment_variable_name is not None:
            self._values["table_environment_variable_name"] = table_environment_variable_name
        if table_permissions is not None:
            self._values["table_permissions"] = table_permissions
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
    def dynamo_table_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps], result)

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
    def existing_table_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        '''Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_table_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default props are used
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    @builtins.property
    def table_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the name of the DynamoDB table.

        :default: - DDB_TABLE_NAME
        '''
        result = self._values.get("table_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_permissions(self) -> typing.Optional[builtins.str]:
        '''Optional table permissions to grant to the Lambda function.

        One of the following may be specified: "All", "Read", "ReadWrite", "Write".

        :default: - Read/write access is given to the Lambda function if no value is specified.
        '''
        result = self._values.get("table_permissions")
        return typing.cast(typing.Optional[builtins.str], result)

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
        return "LambdaToDynamoDBProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToDynamoDB",
    "LambdaToDynamoDBProps",
]

publication.publish()

def _typecheckingstub__092571f3790131920e423b6b48f6ada271812c0ab4c4b76127eec81553b7a3b0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    table_environment_variable_name: typing.Optional[builtins.str] = None,
    table_permissions: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c30a6a57824df9f62e5321acb93af2c3fb40432124ad8139a8da216f3d87fc(
    *,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    table_environment_variable_name: typing.Optional[builtins.str] = None,
    table_permissions: typing.Optional[builtins.str] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
