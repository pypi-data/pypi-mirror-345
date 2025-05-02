r'''
# aws-lambda-kendra module

---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---


| **Reference Documentation**: | <span style="font-weight: normal;">https://docs.aws.amazon.com/solutions/latest/constructs/</span> |
| --- | --- |

| **Language** | **Package** |
| --- | --- |
| ![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python | `aws_solutions_constructs.aws_lambda_kendra` |
| ![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript | `@aws-solutions-constructs/aws-lambda-kendra` |
| ![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java | `software.amazon.awsconstructs.services.lambdakendra` |

## Overview

This AWS Solutions Construct implements an AWS Lambda function and Amazon Kendra index with the least privileged permissions.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps, Aws } from 'aws-cdk-lib';
import { LambdaToKendra } from '@aws-solutions-constructs/aws-lambda-kendra';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as s3 from "aws-cdk-lib/aws-s3";

const lambdaProps: lambda.FunctionProps = {
  code: lambda.Code.fromAsset(`lambda`),
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler'
};

new LambdaToKendra(this, 'sample', {
  lambdaFunctionProps: lambdaProps,
  kendraIndexProps: {},
  kendraDataSourceProps: [{
    type: 'S3',
    dataSourceConfiguration: {
      s3Configuration: {
        bucketName: 'your-bucket-name',
      }
    }
  ],
});
```

Python

```python
TBD
```

Java

```java
TBD
```

## Pattern Construct Props

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| existingLambdaObj? | [`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html) | Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error. |
| lambdaFunctionProps? | [`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.FunctionProps.html) | User provided props to override the default props for the Lambda function. |
| kendraIndexProps? | [`kendra.CfnIndexProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kendra.CfnIndex.html) | Optional user provided props to override the default props for the Kendra index. Providing both these and existingKendraIndexObj is an error. |
| kendraDataSourcesProps | [`CfnDataSourceProps[]`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kendra.CfnDataSource.html) | A list of data sources that will provide data to the Kendra index. *At least 1 must be specified*. We will do majority of processing for some data sources (S3 crawler initially), but for others the props must be complete (e.g. proper roleArn, etc.) |
| indexPermissions? | `string[]` | Optional - index permissions to grant to the Lambda function. One or more of the following may be specified: `Read`, `SubmitFeedback` and `Write`. Default is `["Read", "SubmitFeedback"]`. Read is all the operations IAM defines as Read and List. SubmitFeedback is only the SubmitFeedback action. Write is all the operations IAM defines as Write and Tag. This functionality may be overridden by providing a specific role arn in lambdaFunctionProps |
| existingKendraIndexObj? | [`kendra.cfnIndex`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kendra.CfnIndex.html) | An existing Kendra index to which the Lambda function will be granted access. Supplying along with kendraIndexProps or kendraDataSourceProps will throw an error. |
| existingVpc? | [`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html) | An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html#static-fromwbrlookupscope-id-options) method. |
| vpcProps? | [`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.VpcProps.html) | Optional user provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overridden. If `deployVpc` is not `true` then this property will be ignored. |
| deployVpc? | `boolean` | Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to `true` will deploy the minimal, most private VPC to run the pattern, consisting of (1) one isolated subnet in each Availability Zone used by the CDK program; and (2) `enableDnsHostnames` and `enableDnsSupport` both being set to `true`. If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`. |

## Pattern Properties

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| lambdaFunction | [`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html) | Returns an instance of `lambda.Function` managed by the construct |
| kendraIndex | [`kendra.cfnIndex`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kendra.CfnIndex.html) | Returns an instance of `kendra.cfnIndex` managed by the construct |
| kendraDataSources | DataSourceProperties[] (this interface is defined by Solutions Constructs and described below) | A list of data sources created for this construct/index, each in an object that includes the role for that data source. |
| lambdaRole | [`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html) | The role assumed by the Lambda function |
| vpc? | [`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html) | Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor. |

interface DataSourceProperties {
role?: [`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html),
source: | [`CfnDataSource`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kendra.CfnDataSource.html)
}

## Lambda Function

This pattern requires a lambda function that can access a Kendra index.

## Default settings

Out of the box implementation of the Construct without any overrides will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for Node.js Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * (default) KENDRA_INDEX_ID
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED

### Amazon Kendra Index

* Creates Amazon Kendra endpoint in VPC if appropriate
* Defaults to DEVELOPER_EDITION

**Amazon Kendra DataSources**

* Sets up correct IAM roles to access data for:

  * S3 data sources
  * Which others should we support in MLP? https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html
* Adds each data source to Kendra index

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
import aws_cdk.aws_kendra as _aws_cdk_aws_kendra_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import constructs as _constructs_77d1e7e8


class LambdaToKendra(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-kendra.LambdaToKendra",
):
    '''
    :summary: The LambdaToKendra class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        kendra_data_sources_props: typing.Sequence[typing.Any],
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_kendra_index_obj: typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        index_id_environment_variable_name: typing.Optional[builtins.str] = None,
        index_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        kendra_index_props: typing.Any = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param kendra_data_sources_props: A list of data sources that will provide data to the Kendra index. ?At least 1 must be specified. We will do majority of processing for some data sources (S3 crawler initially), but for others the props must be complete (e.g. proper roleArn, etc.) Default: - empty list (no data sources)
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_kendra_index_obj: Existing instance of a Kendra Index. Providing both this and kendraIndexProps will cause an error. Default: - None
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param index_id_environment_variable_name: Optional Name for the Lambda function environment variable set to the index id for the Kendra index. Default: - KENDRA_INDEX_ID
        :param index_permissions: Optional - index permissions to grant to the Lambda function. One or more of the following may be specified: ``Read``, ``SubmitFeedback`` and ``Write``. Default is ``["Read", "SubmitFeedback"]``. Read is all the operations IAM defines as Read and List. SubmitFeedback is only the SubmitFeedback action. Write is all the operations IAM defines as Write and Tag. This functionality may be overridden by providing a specific role arn in lambdaFunctionProps Default: - ["Read", "SubmitFeedback"]
        :param kendra_index_props: Default: - Optional user provided props to override the default props for the Kendra index. Is this required?
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :since: 1.120.0
        :summary: Constructs a new instance of the LambdaToKendra class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9da37223ecd15aa48c8fdb15e8ae674033a9aa9395fc3369ba9f24ea9cae4ca1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LambdaToKendraProps(
            kendra_data_sources_props=kendra_data_sources_props,
            deploy_vpc=deploy_vpc,
            existing_kendra_index_obj=existing_kendra_index_obj,
            existing_lambda_obj=existing_lambda_obj,
            existing_vpc=existing_vpc,
            index_id_environment_variable_name=index_id_environment_variable_name,
            index_permissions=index_permissions,
            kendra_index_props=kendra_index_props,
            lambda_function_props=lambda_function_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="kendraDataSources")
    def kendra_data_sources(
        self,
    ) -> typing.List[_aws_cdk_aws_kendra_ceddda9d.CfnDataSource]:
        return typing.cast(typing.List[_aws_cdk_aws_kendra_ceddda9d.CfnDataSource], jsii.get(self, "kendraDataSources"))

    @builtins.property
    @jsii.member(jsii_name="kendraIndex")
    def kendra_index(self) -> _aws_cdk_aws_kendra_ceddda9d.CfnIndex:
        return typing.cast(_aws_cdk_aws_kendra_ceddda9d.CfnIndex, jsii.get(self, "kendraIndex"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-kendra.LambdaToKendraProps",
    jsii_struct_bases=[],
    name_mapping={
        "kendra_data_sources_props": "kendraDataSourcesProps",
        "deploy_vpc": "deployVpc",
        "existing_kendra_index_obj": "existingKendraIndexObj",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_vpc": "existingVpc",
        "index_id_environment_variable_name": "indexIdEnvironmentVariableName",
        "index_permissions": "indexPermissions",
        "kendra_index_props": "kendraIndexProps",
        "lambda_function_props": "lambdaFunctionProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToKendraProps:
    def __init__(
        self,
        *,
        kendra_data_sources_props: typing.Sequence[typing.Any],
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_kendra_index_obj: typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        index_id_environment_variable_name: typing.Optional[builtins.str] = None,
        index_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        kendra_index_props: typing.Any = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param kendra_data_sources_props: A list of data sources that will provide data to the Kendra index. ?At least 1 must be specified. We will do majority of processing for some data sources (S3 crawler initially), but for others the props must be complete (e.g. proper roleArn, etc.) Default: - empty list (no data sources)
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_kendra_index_obj: Existing instance of a Kendra Index. Providing both this and kendraIndexProps will cause an error. Default: - None
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param index_id_environment_variable_name: Optional Name for the Lambda function environment variable set to the index id for the Kendra index. Default: - KENDRA_INDEX_ID
        :param index_permissions: Optional - index permissions to grant to the Lambda function. One or more of the following may be specified: ``Read``, ``SubmitFeedback`` and ``Write``. Default is ``["Read", "SubmitFeedback"]``. Read is all the operations IAM defines as Read and List. SubmitFeedback is only the SubmitFeedback action. Write is all the operations IAM defines as Write and Tag. This functionality may be overridden by providing a specific role arn in lambdaFunctionProps Default: - ["Read", "SubmitFeedback"]
        :param kendra_index_props: Default: - Optional user provided props to override the default props for the Kendra index. Is this required?
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToKendra class.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8957f6725b32e539ea465d702d48e3d75f146e27128542a202ab4b9152fe115)
            check_type(argname="argument kendra_data_sources_props", value=kendra_data_sources_props, expected_type=type_hints["kendra_data_sources_props"])
            check_type(argname="argument deploy_vpc", value=deploy_vpc, expected_type=type_hints["deploy_vpc"])
            check_type(argname="argument existing_kendra_index_obj", value=existing_kendra_index_obj, expected_type=type_hints["existing_kendra_index_obj"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument index_id_environment_variable_name", value=index_id_environment_variable_name, expected_type=type_hints["index_id_environment_variable_name"])
            check_type(argname="argument index_permissions", value=index_permissions, expected_type=type_hints["index_permissions"])
            check_type(argname="argument kendra_index_props", value=kendra_index_props, expected_type=type_hints["kendra_index_props"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kendra_data_sources_props": kendra_data_sources_props,
        }
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_kendra_index_obj is not None:
            self._values["existing_kendra_index_obj"] = existing_kendra_index_obj
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if index_id_environment_variable_name is not None:
            self._values["index_id_environment_variable_name"] = index_id_environment_variable_name
        if index_permissions is not None:
            self._values["index_permissions"] = index_permissions
        if kendra_index_props is not None:
            self._values["kendra_index_props"] = kendra_index_props
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def kendra_data_sources_props(self) -> typing.List[typing.Any]:
        '''A list of data sources that will provide data to the Kendra index.

        ?At least 1 must be specified. We will do majority of
        processing for some data sources (S3 crawler initially), but for others the props must be complete (e.g. proper roleArn, etc.)

        :default: - empty list (no data sources)
        '''
        result = self._values.get("kendra_data_sources_props")
        assert result is not None, "Required property 'kendra_data_sources_props' is missing"
        return typing.cast(typing.List[typing.Any], result)

    @builtins.property
    def deploy_vpc(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a new VPC.

        :default: - false
        '''
        result = self._values.get("deploy_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_kendra_index_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex]:
        '''Existing instance of a Kendra Index.

        Providing both this and kendraIndexProps will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_kendra_index_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex], result)

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
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def index_id_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the index id for the Kendra index.

        :default: - KENDRA_INDEX_ID
        '''
        result = self._values.get("index_id_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index_permissions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Optional - index permissions to grant to the Lambda function.

        One or more of the following
        may be specified: ``Read``, ``SubmitFeedback`` and ``Write``. Default is ``["Read", "SubmitFeedback"]``. Read is
        all the operations IAM defines as Read and List. SubmitFeedback is only the SubmitFeedback action. Write is all the
        operations IAM defines as Write and Tag. This functionality may be overridden by providing a specific role arn in lambdaFunctionProps

        :default: - ["Read", "SubmitFeedback"]
        '''
        result = self._values.get("index_permissions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kendra_index_props(self) -> typing.Any:
        '''
        :default: - Optional user provided props to override the default props for the Kendra index. Is this required?
        '''
        result = self._values.get("kendra_index_props")
        return typing.cast(typing.Any, result)

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
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''Properties to override default properties if deployVpc is true.'''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToKendraProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToKendra",
    "LambdaToKendraProps",
]

publication.publish()

def _typecheckingstub__9da37223ecd15aa48c8fdb15e8ae674033a9aa9395fc3369ba9f24ea9cae4ca1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    kendra_data_sources_props: typing.Sequence[typing.Any],
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_kendra_index_obj: typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    index_id_environment_variable_name: typing.Optional[builtins.str] = None,
    index_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
    kendra_index_props: typing.Any = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8957f6725b32e539ea465d702d48e3d75f146e27128542a202ab4b9152fe115(
    *,
    kendra_data_sources_props: typing.Sequence[typing.Any],
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_kendra_index_obj: typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    index_id_environment_variable_name: typing.Optional[builtins.str] = None,
    index_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
    kendra_index_props: typing.Any = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
