r'''
# aws-lambda-bedrockinferenceprofile module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_bedrockinferenceprofile`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-bedrockinferenceprofile`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdabedrockinferenceprofile`|

## Overview

This AWS Solutions Construct implements a Lambda function granted access to a new Bedrock Inference Profile. [Inference profiles](https://aws.amazon.com/blogs/machine-learning/getting-started-with-cross-region-inference-in-amazon-bedrock/) allow:

* Greater scalability of applications by distributing Bedrock Invoke calls across multiple regions
* Cost management by adding Cost Allocation Tags to an inference to track costs for specific applications.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { LambdaToBedrockInferenceProfile } from "@aws-solutions-constructs/aws-lambda-bedrockinferenceprofile";
import * as lambda from 'aws-cdk-lib/aws-lambda';

new LambdaToBedrockInferenceProfile(this, 'LambdaToBedrockPattern', {
    lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_20_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`lambda`)
    },
    model: "amazon.nova-lite-v1:0"
});
```

Python

```python
from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)

from aws_solutions_constructs import (
    aws_lambda_bedrockinferenceprofile as lambda_bedrock
)

lambda_bedrock.LambdaToBedrockinferenceprofile(
    self, 'bedrock-construct',
    bedrock_model_id="amazon.nova-lite-v1:0",
    lambda_function_props=_lambda.FunctionProps(
        runtime=_lambda.Runtime.NODEJS_20_X,
        code=_lambda.Code.from_asset('lambda'),
        handler='index.handler',
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
import software.amazon.awsconstructs.services.lambdabedrockinferenceprofile.*;

  new LambdaToBedrockinferenceprofile(this, "ApiGatewayToLambdaPattern", new LambdaToBedrockinferenceprofileProps.Builder()
          .lambdaFunctionProps(new FunctionProps.Builder()
                  .runtime(Runtime.NODEJS_20_X)
                  .code(Code.fromAsset("lambda"))
                  .handler("index.handler")
                  .build())
          .bedrockModelId("amazon.nova-lite-v1:0")
          .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.FunctionProps.html)|Optional user provided props to override the default props for the Lambda function.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for Amazon Bedrock and Bedrock-Runtime. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.VpcProps.html)|Optional user provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overridden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|
|bedrockModelId|`string`|The foundation model to use with the inference profile. Depending on whether the deployment is cross region or single region, he construct will create the correct inference profile name and and assign IAM permissions to the Lambda function allowing access to the foundation model in all appropriate regions. For all of this to occur, the model must be specified here and *not* in `inferenceProfileProps`. Be certain that the account is granted access to the foundation model in [all the regions covered by the cross-region inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html).|
|inferenceProfileProps?|[`bedrock.CfnApplicationInferenceProfileProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_bedrock.CfnApplicationInferenceProfileProps.html)|This is where you set tags required for tracking inference calls. Do not populate the copyFrom attribute - the construct will populate this based upon the model sent in bedrockModelId (this allows the construct to correctly create all the other dependencies like the required IAM policies). If the copyFrom attribute is supplied here the construct will throw an error. The construct will also set a unique, stack specific inferenceProfileName - you may override that name here, but it is not recommended.
|deployCrossRegionProfile|boolean| Whether to deploy a cross-region inference profile that will automatically distribute Invoke calls across multiple regions. Note that at the time of this writing, cross-region profiles are only available in [US, EMEA and APAC](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html). Single region profiles are available in every region supporting Bedrock models. Defaults to `true`|
|foundationModelEnvironmentVariableName?|string|Optional Name for the Lambda function environment variable set to the Model name. Defaults to BEDROCK_MODEL|
|inferenceProfileEnvironmentVariableName?|string|Optional Name for the Lambda function environment variable set to the inference profile arn. Defaults to BEDROCK_PROFILE|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html)|Returns an instance of the Lambda function created by the pattern.|
|inferenceProfile|[`CfnApplicationInferenceProfile`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_bedrock.CfnApplicationInferenceProfile.html)|The inference profile created by the construct.|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function, granting Invoke privileges for:

  * The new inference profile
  * The appropriate foundation model in all regions in the geographic area. For single region inference profiles, access is only granted to model in the current region.
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * (default) BEDROCK_PROFILE
  * (default) BEDROCK_MODEL

### Amazon Bedrock Inference Profile

* Cross-region inference profile for provided model by default
* Geographic area prefix in arn defaults to value appropriate for deployment region (e.g. would us 'us' for us-east-1 deployment)

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

import aws_cdk.aws_bedrock as _aws_cdk_aws_bedrock_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import constructs as _constructs_77d1e7e8


class LambdaToBedrockinferenceprofile(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-bedrockinferenceprofile.LambdaToBedrockinferenceprofile",
):
    '''
    :summary: The LambdaToBedrockinferenceprofile class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bedrock_model_id: builtins.str,
        deploy_cross_region_profile: typing.Optional[builtins.bool] = None,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        foundation_model_environment_variable_name: typing.Optional[builtins.str] = None,
        inference_profile_environment_variable_name: typing.Optional[builtins.str] = None,
        inference_profile_props: typing.Optional[typing.Union[_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param bedrock_model_id: The foundation model to use with the inference profile. The construct will validate the model name, create the correct inference profile name based on the region and remind the developer in which regions the model must be available for this profile. Be certain that the account is granted access to the foundation model in all the regions covered by cross-region inference profile
        :param deploy_cross_region_profile: Whether to deploy a cross-region inference profile that will automatically distribute Invoke calls across multiple regions. Default: - true
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param foundation_model_environment_variable_name: Optional Name for the Lambda function environment variable set to the Model name. Default: - BEDROCK_MODEL
        :param inference_profile_environment_variable_name: Optional Name for the Lambda function environment variable set to the inference profile arn. Default: - BEDROCK_PROFILE
        :param inference_profile_props: Properties to override constructs props values for the Inference Profile. The construct will populate inverenceProfileName - so don't override it unless you have an very good reason. The construct base IAM policies around the modelSource that it creates, so trying to send a modelSource in ths parameter will cause an error. This is where you set tags required for tracking inference calls.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the LambdaToSns class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f146eecba713ed1ed7bed25607c92b6cdce670262bf0c10ad465027e80d1370)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LambdaToBedrockinferenceprofileProps(
            bedrock_model_id=bedrock_model_id,
            deploy_cross_region_profile=deploy_cross_region_profile,
            deploy_vpc=deploy_vpc,
            existing_lambda_obj=existing_lambda_obj,
            existing_vpc=existing_vpc,
            foundation_model_environment_variable_name=foundation_model_environment_variable_name,
            inference_profile_environment_variable_name=inference_profile_environment_variable_name,
            inference_profile_props=inference_profile_props,
            lambda_function_props=lambda_function_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="inferenceProfile")
    def inference_profile(
        self,
    ) -> _aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfile:
        return typing.cast(_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfile, jsii.get(self, "inferenceProfile"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-bedrockinferenceprofile.LambdaToBedrockinferenceprofileProps",
    jsii_struct_bases=[],
    name_mapping={
        "bedrock_model_id": "bedrockModelId",
        "deploy_cross_region_profile": "deployCrossRegionProfile",
        "deploy_vpc": "deployVpc",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_vpc": "existingVpc",
        "foundation_model_environment_variable_name": "foundationModelEnvironmentVariableName",
        "inference_profile_environment_variable_name": "inferenceProfileEnvironmentVariableName",
        "inference_profile_props": "inferenceProfileProps",
        "lambda_function_props": "lambdaFunctionProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToBedrockinferenceprofileProps:
    def __init__(
        self,
        *,
        bedrock_model_id: builtins.str,
        deploy_cross_region_profile: typing.Optional[builtins.bool] = None,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        foundation_model_environment_variable_name: typing.Optional[builtins.str] = None,
        inference_profile_environment_variable_name: typing.Optional[builtins.str] = None,
        inference_profile_props: typing.Optional[typing.Union[_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bedrock_model_id: The foundation model to use with the inference profile. The construct will validate the model name, create the correct inference profile name based on the region and remind the developer in which regions the model must be available for this profile. Be certain that the account is granted access to the foundation model in all the regions covered by cross-region inference profile
        :param deploy_cross_region_profile: Whether to deploy a cross-region inference profile that will automatically distribute Invoke calls across multiple regions. Default: - true
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param foundation_model_environment_variable_name: Optional Name for the Lambda function environment variable set to the Model name. Default: - BEDROCK_MODEL
        :param inference_profile_environment_variable_name: Optional Name for the Lambda function environment variable set to the inference profile arn. Default: - BEDROCK_PROFILE
        :param inference_profile_props: Properties to override constructs props values for the Inference Profile. The construct will populate inverenceProfileName - so don't override it unless you have an very good reason. The construct base IAM policies around the modelSource that it creates, so trying to send a modelSource in ths parameter will cause an error. This is where you set tags required for tracking inference calls.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToSns class.
        '''
        if isinstance(inference_profile_props, dict):
            inference_profile_props = _aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps(**inference_profile_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbd286561a19e8bd53f160f75f50f6ccc70ee89235d93c7e43431b10d35bd16c)
            check_type(argname="argument bedrock_model_id", value=bedrock_model_id, expected_type=type_hints["bedrock_model_id"])
            check_type(argname="argument deploy_cross_region_profile", value=deploy_cross_region_profile, expected_type=type_hints["deploy_cross_region_profile"])
            check_type(argname="argument deploy_vpc", value=deploy_vpc, expected_type=type_hints["deploy_vpc"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument foundation_model_environment_variable_name", value=foundation_model_environment_variable_name, expected_type=type_hints["foundation_model_environment_variable_name"])
            check_type(argname="argument inference_profile_environment_variable_name", value=inference_profile_environment_variable_name, expected_type=type_hints["inference_profile_environment_variable_name"])
            check_type(argname="argument inference_profile_props", value=inference_profile_props, expected_type=type_hints["inference_profile_props"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bedrock_model_id": bedrock_model_id,
        }
        if deploy_cross_region_profile is not None:
            self._values["deploy_cross_region_profile"] = deploy_cross_region_profile
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if foundation_model_environment_variable_name is not None:
            self._values["foundation_model_environment_variable_name"] = foundation_model_environment_variable_name
        if inference_profile_environment_variable_name is not None:
            self._values["inference_profile_environment_variable_name"] = inference_profile_environment_variable_name
        if inference_profile_props is not None:
            self._values["inference_profile_props"] = inference_profile_props
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def bedrock_model_id(self) -> builtins.str:
        '''The foundation model to use with the inference profile.

        The construct
        will validate the model name, create the correct inference profile name
        based on the region and remind the developer in which regions the model
        must be available for this profile. Be certain that the account is granted
        access to the foundation model in all the regions covered by cross-region
        inference profile
        '''
        result = self._values.get("bedrock_model_id")
        assert result is not None, "Required property 'bedrock_model_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deploy_cross_region_profile(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a cross-region inference profile that will automatically distribute Invoke calls across multiple regions.

        :default: - true
        '''
        result = self._values.get("deploy_cross_region_profile")
        return typing.cast(typing.Optional[builtins.bool], result)

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
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def foundation_model_environment_variable_name(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the Model name.

        :default: - BEDROCK_MODEL
        '''
        result = self._values.get("foundation_model_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_profile_environment_variable_name(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the inference profile arn.

        :default: - BEDROCK_PROFILE
        '''
        result = self._values.get("inference_profile_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_profile_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps]:
        '''Properties to override constructs props values for the Inference Profile.

        The construct will populate inverenceProfileName - so don't override it
        unless you have an very good reason.  The construct base IAM policies around
        the modelSource that it creates, so trying to send a modelSource in ths
        parameter will cause an error. This is where you set tags required for
        tracking inference calls.
        '''
        result = self._values.get("inference_profile_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps], result)

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
        return "LambdaToBedrockinferenceprofileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToBedrockinferenceprofile",
    "LambdaToBedrockinferenceprofileProps",
]

publication.publish()

def _typecheckingstub__3f146eecba713ed1ed7bed25607c92b6cdce670262bf0c10ad465027e80d1370(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bedrock_model_id: builtins.str,
    deploy_cross_region_profile: typing.Optional[builtins.bool] = None,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    foundation_model_environment_variable_name: typing.Optional[builtins.str] = None,
    inference_profile_environment_variable_name: typing.Optional[builtins.str] = None,
    inference_profile_props: typing.Optional[typing.Union[_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbd286561a19e8bd53f160f75f50f6ccc70ee89235d93c7e43431b10d35bd16c(
    *,
    bedrock_model_id: builtins.str,
    deploy_cross_region_profile: typing.Optional[builtins.bool] = None,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    foundation_model_environment_variable_name: typing.Optional[builtins.str] = None,
    inference_profile_environment_variable_name: typing.Optional[builtins.str] = None,
    inference_profile_props: typing.Optional[typing.Union[_aws_cdk_aws_bedrock_ceddda9d.CfnApplicationInferenceProfileProps, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
