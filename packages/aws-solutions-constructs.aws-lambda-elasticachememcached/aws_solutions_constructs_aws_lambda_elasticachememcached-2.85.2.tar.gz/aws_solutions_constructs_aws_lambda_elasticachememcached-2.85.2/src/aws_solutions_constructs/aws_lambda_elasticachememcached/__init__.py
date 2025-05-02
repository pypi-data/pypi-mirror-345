r'''
# aws-lambda-elasticachememcached module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_elasticachememcached`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-elasticachememcached`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdaelasticachememcached`|

## Overview

This AWS Solutions Construct implements an AWS Lambda function connected to an Amazon Elasticache Memcached cluster.

Here is a minimal deployable pattern definition :

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { LambdaToElasticachememcached } from '@aws-solutions-constructs/aws-lambda-elasticachememcached';
import * as lambda from 'aws-cdk-lib/aws-lambda';

new LambdaToElasticachememcached(this, 'LambdaToElasticachememcachedPattern', {
    lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_20_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`lambda`)
    }
});
```

Python

```python
from aws_solutions_constructs.aws_lambda_elasticachememcached import LambdaToElasticachememcached
from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)
from constructs import Construct

LambdaToElasticachememcached(self, 'LambdaToCachePattern',
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
import software.amazon.awsconstructs.services.lambdaelasticachememcached.*;

new LambdaToElasticachememcached(this, "LambdaToCachePattern", new LambdaToElasticachememcachedProps.Builder()
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
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.FunctionProps.html)|Optional user provided props to override the default props for the Lambda function.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for Amazon Elasticache. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.VpcProps.html)|Optional user provided properties to override the default properties for the new VPC. `subnetConfiguration` is set by the pattern, so any values for those properties supplied here will be overridden. |
| cacheEndpointEnvironmentVariableName?| string | Optional Name for the Lambda function environment variable set to the cache endpoint. Default: CACHE_ENDPOINT |
| cacheProps? | [`cache.CfnCacheClusterProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticache.CfnCacheClusterProps.html) | Optional user provided props to override the default props for the Elasticache Cluster. Providing both this and `existingCache` will cause an error. |
| existingCache? | [`cache.CfnCacheCluster`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticache.CfnCacheCluster.html#attrconfigurationendpointport) | Existing instance of Elasticache Cluster object, providing both this and `cacheProps` will cause an error. If you provide this, you must provide the associated VPC in existingVpc. |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html)|Returns an instance of the Lambda function used by the pattern.|
|vpc |[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|Returns an interface on the VPC used by the pattern. This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|
| cache | [`cache.CfnCacheCluster`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticache.CfnCacheCluster.html#attrconfigurationendpointport) | The Elasticache Memcached cluster used by the construct. |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Attached to self referencing security group to grant access to cache
* Set Environment Variables

  * (default) CACHE_ENDPOINT
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon Elasticache Memcached Cluster

* Creates multi node, cross-az cluster by default

  * 2 cache nodes, type: cache.t3.medium
* Self referencing security group attached to cluster endpoint

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
import aws_cdk.aws_elasticache as _aws_cdk_aws_elasticache_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import constructs as _constructs_77d1e7e8


class LambdaToElasticachememcached(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-elasticachememcached.LambdaToElasticachememcached",
):
    '''
    :summary: The LambdaToElasticachememcached class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cache_endpoint_environment_variable_name: typing.Optional[builtins.str] = None,
        cache_props: typing.Any = None,
        existing_cache: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cache_endpoint_environment_variable_name: Optional Name for the Lambda function environment variable set to the cache endpoint. Default: - CACHE_ENDPOINT
        :param cache_props: Optional user provided props to override the default props for the Elasticache cache. Providing both this and ``existingCache`` will cause an error. If you provide this, you must provide the associated VPC in existingVpc. Default: - Default properties are used (core/lib/elasticacahe-defaults.ts)
        :param existing_cache: Existing instance of Elasticache Cluster object, providing both this and ``cacheProps`` will cause an error. Default: - none
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case). Default: - none
        :param lambda_function_props: Optional user provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true. Default: - DefaultIsolatedVpcProps() in vpc-defaults.ts

        :access: public
        :summary: Constructs a new instance of the LambdaToElasticachememcached class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9839f737b99fce32b9fe35e48df7f778fd78cb8ea7d9d44af8828e8277cdfed4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LambdaToElasticachememcachedProps(
            cache_endpoint_environment_variable_name=cache_endpoint_environment_variable_name,
            cache_props=cache_props,
            existing_cache=existing_cache,
            existing_lambda_obj=existing_lambda_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="cache")
    def cache(self) -> _aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster:
        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster, jsii.get(self, "cache"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-elasticachememcached.LambdaToElasticachememcachedProps",
    jsii_struct_bases=[],
    name_mapping={
        "cache_endpoint_environment_variable_name": "cacheEndpointEnvironmentVariableName",
        "cache_props": "cacheProps",
        "existing_cache": "existingCache",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToElasticachememcachedProps:
    def __init__(
        self,
        *,
        cache_endpoint_environment_variable_name: typing.Optional[builtins.str] = None,
        cache_props: typing.Any = None,
        existing_cache: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cache_endpoint_environment_variable_name: Optional Name for the Lambda function environment variable set to the cache endpoint. Default: - CACHE_ENDPOINT
        :param cache_props: Optional user provided props to override the default props for the Elasticache cache. Providing both this and ``existingCache`` will cause an error. If you provide this, you must provide the associated VPC in existingVpc. Default: - Default properties are used (core/lib/elasticacahe-defaults.ts)
        :param existing_cache: Existing instance of Elasticache Cluster object, providing both this and ``cacheProps`` will cause an error. Default: - none
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case). Default: - none
        :param lambda_function_props: Optional user provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true. Default: - DefaultIsolatedVpcProps() in vpc-defaults.ts

        :summary: The properties for the LambdaToElasticachememcached class.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be5112c9f409f0761d2af51f178f83dc585cee7d02815e1150d8a47e9df3b4da)
            check_type(argname="argument cache_endpoint_environment_variable_name", value=cache_endpoint_environment_variable_name, expected_type=type_hints["cache_endpoint_environment_variable_name"])
            check_type(argname="argument cache_props", value=cache_props, expected_type=type_hints["cache_props"])
            check_type(argname="argument existing_cache", value=existing_cache, expected_type=type_hints["existing_cache"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cache_endpoint_environment_variable_name is not None:
            self._values["cache_endpoint_environment_variable_name"] = cache_endpoint_environment_variable_name
        if cache_props is not None:
            self._values["cache_props"] = cache_props
        if existing_cache is not None:
            self._values["existing_cache"] = existing_cache
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def cache_endpoint_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the cache endpoint.

        :default: - CACHE_ENDPOINT
        '''
        result = self._values.get("cache_endpoint_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_props(self) -> typing.Any:
        '''Optional user provided props to override the default props for the Elasticache cache.

        Providing both this and ``existingCache`` will cause an error.  If you provide this,
        you must provide the associated VPC in existingVpc.

        :default: - Default properties are used (core/lib/elasticacahe-defaults.ts)
        '''
        result = self._values.get("cache_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def existing_cache(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster]:
        '''Existing instance of Elasticache Cluster object, providing both this and ``cacheProps`` will cause an error.

        :default: - none
        '''
        result = self._values.get("existing_cache")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster], result)

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
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).

        :default: - none
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''Optional user provided props to override the default props for the Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''Properties to override default properties if deployVpc is true.

        :default: - DefaultIsolatedVpcProps() in vpc-defaults.ts
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToElasticachememcachedProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToElasticachememcached",
    "LambdaToElasticachememcachedProps",
]

publication.publish()

def _typecheckingstub__9839f737b99fce32b9fe35e48df7f778fd78cb8ea7d9d44af8828e8277cdfed4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cache_endpoint_environment_variable_name: typing.Optional[builtins.str] = None,
    cache_props: typing.Any = None,
    existing_cache: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be5112c9f409f0761d2af51f178f83dc585cee7d02815e1150d8a47e9df3b4da(
    *,
    cache_endpoint_environment_variable_name: typing.Optional[builtins.str] = None,
    cache_props: typing.Any = None,
    existing_cache: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
