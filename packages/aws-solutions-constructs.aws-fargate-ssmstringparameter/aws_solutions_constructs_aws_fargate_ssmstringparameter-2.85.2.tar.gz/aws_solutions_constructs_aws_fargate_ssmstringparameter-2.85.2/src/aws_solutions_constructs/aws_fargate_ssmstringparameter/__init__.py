r'''
# aws-fargate-ssmstringparameter module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_fargate_ssmstringparameter`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-fargate-ssmstringparameter`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.fargatessmstringparameter`|

## Overview

This AWS Solutions Construct implements an AWS Fargate service that can read/write to an AWS Systems Manager String Parameter

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { FargateToSsmstringparameter, FargateToSsmstringparameterProps } from '@aws-solutions-constructs/aws-fargate-ssmstringparameter';

const constructProps: FargateToSsmstringparameterProps = {
  publicApi: true,
  ecrRepositoryArn: "arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo",
  stringParameterProps: { stringValue: "test-string-value" }
};

new FargateToSsmstringparameter(stack, 'test-construct', constructProps);
```

Python

```python
from aws_solutions_constructs.aws_fargate_ssmstringparameter import FargateToSsmstringparameter, FargateToSsmstringparameterProps
from aws_cdk import (
    Stack,
    aws_ssm as ssm
)
from constructs import Construct

FargateToSsmstringparameter(self, 'test_construct',
            public_api=True,
            ecr_repository_arn="arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo",
            string_parameter_props=ssm.StringParameterProps(
              string_value="test-string-value"))
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.services.ssm.*;
import software.amazon.awsconstructs.services.fargatessmstringparameter.*;

new FargateToSsmstringparameter(this, "test-construct", new FargateToSsmstringparameterProps.Builder()
        .publicApi(true)
        .ecrRepositoryArn("arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo")
        .stringParameterProps(new StringParameterProps.Builder()
                        .stringValue("test-string-value")
                        .build())
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| publicApi | `boolean` | Whether the construct is deploying a private or public API. This has implications for the VPC. |
| vpcProps? | [`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.VpcProps.html) | Optional custom properties for a VPC the construct will create. This VPC will be used by any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. |
| existingVpc? | [`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html) | An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. |
| clusterProps? | [`ecs.ClusterProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.ClusterProps.html) | Optional properties to create a new ECS cluster. To provide an existing cluster, use the cluster attribute of fargateServiceProps. |
| ecrRepositoryArn? | `string` | The arn of an ECR Repository containing the image to use to generate the containers. Either this or the image property of containerDefinitionProps must be provided. format: arn:aws:ecr:*region*:*account number*:repository/*Repository Name* |
| ecrImageVersion? | `string` | The version of the image to use from the repository. Defaults to 'Latest' |
| containerDefinitionProps? | [`ecs.ContainerDefinitionProps \| any`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.ContainerDefinitionProps.html) | Optional props to define the container created for the Fargate Service (defaults found in fargate-defaults.ts) |
| fargateTaskDefinitionProps? | [`ecs.FargateTaskDefinitionProps \| any`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateTaskDefinitionProps.html) | Optional props to define the Fargate Task Definition for this construct  (defaults found in fargate-defaults.ts) |
| fargateServiceProps? | [`ecs.FargateServiceProps \| any`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateServiceProps.html) | Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here. |
| existingFargateServiceObject? | [`ecs.FargateService`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateService.html) | A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: ecrImageVersion, containerDefinitionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps |
| existingContainerDefinitionObject? | [`ecs.ContainerDefinition`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.ContainerDefinition.html) | A container definition already instantiated as part of a Fargate service. This must be the container in the existingFargateServiceObject |
|existingStringParameterObj?|[`ssm.StringParameter`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ssm.StringParameter.html)|Existing instance of SSM String parameter object, providing both this and `stringParameterProps` will cause an error|
|stringParameterProps?|[`ssm.StringParameterProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ssm.StringParameterProps.html)|Optional user provided props to override the default props for SSM String parameter. If existingStringParameterObj is not set stringParameterProps is required. The only supported [`ssm.StringParameterProps.type`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ssm.StringParameterProps.html#type) is [`STRING`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ssm.ParameterType.html#string) if a different value is provided it will be overridden.|
|stringParameterPermissions?|`string`|Optional SSM String parameter permissions to grant to the Fargate service. One of the following may be specified: "Read", "ReadWrite".
|stringParameterEnvironmentVariableName?|`string`|Optional Name for the container environment variable set to the SSM parameter name. Default: SSM_STRING_PARAMETER_NAME |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| vpc | [`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html) | The VPC used by the construct (whether created by the construct or provided by the client) |
| service | [`ecs.FargateService`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateService.html) | The AWS Fargate service used by this construct (whether created by this construct or passed to this construct at initialization) |
| container | [`ecs.ContainerDefinition`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.ContainerDefinition.html) | The container associated with the AWS Fargate service in the service property. |
|stringParameter|[`ssm.StringParameter`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ssm.StringParameter.html)|Returns an instance of `ssm.StringParameter` created by the construct|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Fargate Service

* Sets up an AWS Fargate service

  * Uses the existing service if provided
  * Creates a new service if none provided.

    * Service will run in isolated subnets if available, then private subnets if available and finally public subnets
  * Adds environment variables to the container with the ARN and Name of the SSM parameter
  * Add permissions to the container IAM role allowing it to read/write to the SSM parameter

### AWS SSM String Parameter

* Sets up an AWS SSM String Parameter

  * Uses an existing parameter if one is provided, otherwise creates a new one
* Adds an Interface Endpoint to the VPC for SSM parameter (the service by default runs in Isolated or Private subnets)

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
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_ssm as _aws_cdk_aws_ssm_ceddda9d
import constructs as _constructs_77d1e7e8


class FargateToSsmstringparameter(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-fargate-ssmstringparameter.FargateToSsmstringparameter",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        public_api: builtins.bool,
        cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        container_definition_props: typing.Any = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
        existing_container_definition_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition] = None,
        existing_fargate_service_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateService] = None,
        existing_string_parameter_obj: typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameter] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        fargate_service_props: typing.Any = None,
        fargate_task_definition_props: typing.Any = None,
        string_parameter_environment_variable_name: typing.Optional[builtins.str] = None,
        string_parameter_permissions: typing.Optional[builtins.str] = None,
        string_parameter_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.StringParameterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC deployed by this construct.
        :param cluster_props: Optional properties to create a new ECS cluster.
        :param container_definition_props: -
        :param ecr_image_version: The version of the image to use from the repository. Default: - 'latest'
        :param ecr_repository_arn: The arn of an ECR Repository containing the image to use to generate the containers. format: arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        :param existing_container_definition_object: -
        :param existing_fargate_service_object: A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: existingImageObject, ecrImageVersion, containerDefinitionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface. If this value is provided, then existingContainerDefinitionObject must be provided as well. Default: - none
        :param existing_string_parameter_obj: Optional user provided props to override the default props for SSM String Parameter. Default: - None
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing Fargate service, this value must be the VPC where the service is running. An SSM Interface endpoint will be added to this VPC. Default: - none
        :param fargate_service_props: Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here. defaults - fargate-defaults.ts
        :param fargate_task_definition_props: -
        :param string_parameter_environment_variable_name: Optional Name for the container environment variable set to the SSM parameter name. Default: - SSM_STRING_PARAMETER_NAME
        :param string_parameter_permissions: Optional SSM String parameter permissions to grant to the Fargate service. One of the following may be specified: "Read", "ReadWrite". Default: - 'Read'
        :param string_parameter_props: Optional user provided props to override the default props for SSM String Parameter. Default: - Default props are used
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new Fargate service the construct creates (that's why targetGroupProps can't include a VPC). Providing both this and existingVpc is an error. An SSM Interface endpoint will be included in this VPC. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db42bcb553184ef618c1b693456f9b8bebd57919b8ed5ab0b7a6eb467725f052)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FargateToSsmstringparameterProps(
            public_api=public_api,
            cluster_props=cluster_props,
            container_definition_props=container_definition_props,
            ecr_image_version=ecr_image_version,
            ecr_repository_arn=ecr_repository_arn,
            existing_container_definition_object=existing_container_definition_object,
            existing_fargate_service_object=existing_fargate_service_object,
            existing_string_parameter_obj=existing_string_parameter_obj,
            existing_vpc=existing_vpc,
            fargate_service_props=fargate_service_props,
            fargate_task_definition_props=fargate_task_definition_props,
            string_parameter_environment_variable_name=string_parameter_environment_variable_name,
            string_parameter_permissions=string_parameter_permissions,
            string_parameter_props=string_parameter_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="container")
    def container(self) -> _aws_cdk_aws_ecs_ceddda9d.ContainerDefinition:
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition, jsii.get(self, "container"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateService:
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateService, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="stringParameter")
    def string_parameter(self) -> _aws_cdk_aws_ssm_ceddda9d.StringParameter:
        return typing.cast(_aws_cdk_aws_ssm_ceddda9d.StringParameter, jsii.get(self, "stringParameter"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-fargate-ssmstringparameter.FargateToSsmstringparameterProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_api": "publicApi",
        "cluster_props": "clusterProps",
        "container_definition_props": "containerDefinitionProps",
        "ecr_image_version": "ecrImageVersion",
        "ecr_repository_arn": "ecrRepositoryArn",
        "existing_container_definition_object": "existingContainerDefinitionObject",
        "existing_fargate_service_object": "existingFargateServiceObject",
        "existing_string_parameter_obj": "existingStringParameterObj",
        "existing_vpc": "existingVpc",
        "fargate_service_props": "fargateServiceProps",
        "fargate_task_definition_props": "fargateTaskDefinitionProps",
        "string_parameter_environment_variable_name": "stringParameterEnvironmentVariableName",
        "string_parameter_permissions": "stringParameterPermissions",
        "string_parameter_props": "stringParameterProps",
        "vpc_props": "vpcProps",
    },
)
class FargateToSsmstringparameterProps:
    def __init__(
        self,
        *,
        public_api: builtins.bool,
        cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        container_definition_props: typing.Any = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
        existing_container_definition_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition] = None,
        existing_fargate_service_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateService] = None,
        existing_string_parameter_obj: typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameter] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        fargate_service_props: typing.Any = None,
        fargate_task_definition_props: typing.Any = None,
        string_parameter_environment_variable_name: typing.Optional[builtins.str] = None,
        string_parameter_permissions: typing.Optional[builtins.str] = None,
        string_parameter_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.StringParameterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC deployed by this construct.
        :param cluster_props: Optional properties to create a new ECS cluster.
        :param container_definition_props: -
        :param ecr_image_version: The version of the image to use from the repository. Default: - 'latest'
        :param ecr_repository_arn: The arn of an ECR Repository containing the image to use to generate the containers. format: arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        :param existing_container_definition_object: -
        :param existing_fargate_service_object: A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: existingImageObject, ecrImageVersion, containerDefinitionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface. If this value is provided, then existingContainerDefinitionObject must be provided as well. Default: - none
        :param existing_string_parameter_obj: Optional user provided props to override the default props for SSM String Parameter. Default: - None
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing Fargate service, this value must be the VPC where the service is running. An SSM Interface endpoint will be added to this VPC. Default: - none
        :param fargate_service_props: Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here. defaults - fargate-defaults.ts
        :param fargate_task_definition_props: -
        :param string_parameter_environment_variable_name: Optional Name for the container environment variable set to the SSM parameter name. Default: - SSM_STRING_PARAMETER_NAME
        :param string_parameter_permissions: Optional SSM String parameter permissions to grant to the Fargate service. One of the following may be specified: "Read", "ReadWrite". Default: - 'Read'
        :param string_parameter_props: Optional user provided props to override the default props for SSM String Parameter. Default: - Default props are used
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new Fargate service the construct creates (that's why targetGroupProps can't include a VPC). Providing both this and existingVpc is an error. An SSM Interface endpoint will be included in this VPC. Default: - none
        '''
        if isinstance(cluster_props, dict):
            cluster_props = _aws_cdk_aws_ecs_ceddda9d.ClusterProps(**cluster_props)
        if isinstance(string_parameter_props, dict):
            string_parameter_props = _aws_cdk_aws_ssm_ceddda9d.StringParameterProps(**string_parameter_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caa683fe07aab9dc3ac6ee6367892d6ba71ebf979550a3b2fe6fe4d66b60973a)
            check_type(argname="argument public_api", value=public_api, expected_type=type_hints["public_api"])
            check_type(argname="argument cluster_props", value=cluster_props, expected_type=type_hints["cluster_props"])
            check_type(argname="argument container_definition_props", value=container_definition_props, expected_type=type_hints["container_definition_props"])
            check_type(argname="argument ecr_image_version", value=ecr_image_version, expected_type=type_hints["ecr_image_version"])
            check_type(argname="argument ecr_repository_arn", value=ecr_repository_arn, expected_type=type_hints["ecr_repository_arn"])
            check_type(argname="argument existing_container_definition_object", value=existing_container_definition_object, expected_type=type_hints["existing_container_definition_object"])
            check_type(argname="argument existing_fargate_service_object", value=existing_fargate_service_object, expected_type=type_hints["existing_fargate_service_object"])
            check_type(argname="argument existing_string_parameter_obj", value=existing_string_parameter_obj, expected_type=type_hints["existing_string_parameter_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument fargate_service_props", value=fargate_service_props, expected_type=type_hints["fargate_service_props"])
            check_type(argname="argument fargate_task_definition_props", value=fargate_task_definition_props, expected_type=type_hints["fargate_task_definition_props"])
            check_type(argname="argument string_parameter_environment_variable_name", value=string_parameter_environment_variable_name, expected_type=type_hints["string_parameter_environment_variable_name"])
            check_type(argname="argument string_parameter_permissions", value=string_parameter_permissions, expected_type=type_hints["string_parameter_permissions"])
            check_type(argname="argument string_parameter_props", value=string_parameter_props, expected_type=type_hints["string_parameter_props"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "public_api": public_api,
        }
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if container_definition_props is not None:
            self._values["container_definition_props"] = container_definition_props
        if ecr_image_version is not None:
            self._values["ecr_image_version"] = ecr_image_version
        if ecr_repository_arn is not None:
            self._values["ecr_repository_arn"] = ecr_repository_arn
        if existing_container_definition_object is not None:
            self._values["existing_container_definition_object"] = existing_container_definition_object
        if existing_fargate_service_object is not None:
            self._values["existing_fargate_service_object"] = existing_fargate_service_object
        if existing_string_parameter_obj is not None:
            self._values["existing_string_parameter_obj"] = existing_string_parameter_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if fargate_service_props is not None:
            self._values["fargate_service_props"] = fargate_service_props
        if fargate_task_definition_props is not None:
            self._values["fargate_task_definition_props"] = fargate_task_definition_props
        if string_parameter_environment_variable_name is not None:
            self._values["string_parameter_environment_variable_name"] = string_parameter_environment_variable_name
        if string_parameter_permissions is not None:
            self._values["string_parameter_permissions"] = string_parameter_permissions
        if string_parameter_props is not None:
            self._values["string_parameter_props"] = string_parameter_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def public_api(self) -> builtins.bool:
        '''Whether the construct is deploying a private or public API.

        This has implications for the VPC deployed
        by this construct.
        '''
        result = self._values.get("public_api")
        assert result is not None, "Required property 'public_api' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ClusterProps]:
        '''Optional properties to create a new ECS cluster.'''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ClusterProps], result)

    @builtins.property
    def container_definition_props(self) -> typing.Any:
        result = self._values.get("container_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def ecr_image_version(self) -> typing.Optional[builtins.str]:
        '''The version of the image to use from the repository.

        :default: - 'latest'
        '''
        result = self._values.get("ecr_image_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecr_repository_arn(self) -> typing.Optional[builtins.str]:
        '''The arn of an ECR Repository containing the image to use to generate the containers.

        format:
        arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        '''
        result = self._values.get("ecr_repository_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_container_definition_object(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition]:
        result = self._values.get("existing_container_definition_object")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition], result)

    @builtins.property
    def existing_fargate_service_object(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateService]:
        '''A Fargate Service already instantiated (probably by another Solutions Construct).

        If
        this is specified, then no props defining a new service can be provided, including:
        existingImageObject, ecrImageVersion, containerDefinitionProps, fargateTaskDefinitionProps,
        ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface. If this value
        is provided, then existingContainerDefinitionObject must be provided as well.

        :default: - none
        '''
        result = self._values.get("existing_fargate_service_object")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateService], result)

    @builtins.property
    def existing_string_parameter_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameter]:
        '''Optional user provided props to override the default props for SSM String Parameter.

        :default: - None
        '''
        result = self._values.get("existing_string_parameter_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameter], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''An existing VPC in which to deploy the construct.

        Providing both this and
        vpcProps is an error. If the client provides an existing Fargate service,
        this value must be the VPC where the service is running. An SSM Interface
        endpoint will be added to this VPC.

        :default: - none
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def fargate_service_props(self) -> typing.Any:
        '''Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here.

        defaults - fargate-defaults.ts
        '''
        result = self._values.get("fargate_service_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def fargate_task_definition_props(self) -> typing.Any:
        result = self._values.get("fargate_task_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def string_parameter_environment_variable_name(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Optional Name for the container environment variable set to the SSM parameter name.

        :default: - SSM_STRING_PARAMETER_NAME
        '''
        result = self._values.get("string_parameter_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def string_parameter_permissions(self) -> typing.Optional[builtins.str]:
        '''Optional SSM String parameter permissions to grant to the Fargate service.

        One of the following may be specified: "Read", "ReadWrite".

        :default: - 'Read'
        '''
        result = self._values.get("string_parameter_permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def string_parameter_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameterProps]:
        '''Optional user provided props to override the default props for SSM String Parameter.

        :default: - Default props are used
        '''
        result = self._values.get("string_parameter_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameterProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''Optional custom properties for a VPC the construct will create.

        This VPC will
        be used by the new Fargate service the construct creates (that's
        why targetGroupProps can't include a VPC). Providing
        both this and existingVpc is an error. An SSM Interface
        endpoint will be included in this VPC.

        :default: - none
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateToSsmstringparameterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FargateToSsmstringparameter",
    "FargateToSsmstringparameterProps",
]

publication.publish()

def _typecheckingstub__db42bcb553184ef618c1b693456f9b8bebd57919b8ed5ab0b7a6eb467725f052(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    public_api: builtins.bool,
    cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    container_definition_props: typing.Any = None,
    ecr_image_version: typing.Optional[builtins.str] = None,
    ecr_repository_arn: typing.Optional[builtins.str] = None,
    existing_container_definition_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition] = None,
    existing_fargate_service_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateService] = None,
    existing_string_parameter_obj: typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameter] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    fargate_service_props: typing.Any = None,
    fargate_task_definition_props: typing.Any = None,
    string_parameter_environment_variable_name: typing.Optional[builtins.str] = None,
    string_parameter_permissions: typing.Optional[builtins.str] = None,
    string_parameter_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.StringParameterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caa683fe07aab9dc3ac6ee6367892d6ba71ebf979550a3b2fe6fe4d66b60973a(
    *,
    public_api: builtins.bool,
    cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    container_definition_props: typing.Any = None,
    ecr_image_version: typing.Optional[builtins.str] = None,
    ecr_repository_arn: typing.Optional[builtins.str] = None,
    existing_container_definition_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition] = None,
    existing_fargate_service_object: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateService] = None,
    existing_string_parameter_obj: typing.Optional[_aws_cdk_aws_ssm_ceddda9d.StringParameter] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    fargate_service_props: typing.Any = None,
    fargate_task_definition_props: typing.Any = None,
    string_parameter_environment_variable_name: typing.Optional[builtins.str] = None,
    string_parameter_permissions: typing.Optional[builtins.str] = None,
    string_parameter_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.StringParameterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
