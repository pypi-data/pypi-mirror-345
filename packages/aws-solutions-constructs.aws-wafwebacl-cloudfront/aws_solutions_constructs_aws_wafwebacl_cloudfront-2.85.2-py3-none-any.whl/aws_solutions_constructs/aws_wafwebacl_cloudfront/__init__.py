r'''
# aws-wafwebacl-cloudfront module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_wafwebacl_cloudfront`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-wafwebacl-cloudfront`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.wafwebaclcloudfront`|

## Overview

This AWS Solutions Construct implements an AWS WAF web ACL connected to Amazon CloudFront.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { CloudFrontToS3 } from '@aws-solutions-constructs/aws-cloudfront-s3';
import { WafwebaclToCloudFront } from "@aws-solutions-constructs/aws-wafwebacl-cloudfront";

const cloudfrontToS3 = new CloudFrontToS3(this, 'test-cloudfront-s3', {});

// This construct can only be attached to a configured CloudFront.
new WafwebaclToCloudFront(this, 'test-wafwebacl-cloudfront', {
    existingCloudFrontWebDistribution: cloudfrontToS3.cloudFrontWebDistribution
});
```

Python

```python
from aws_solutions_constructs.aws_cloudfront_s3 import CloudFrontToS3
from aws_solutions_constructs.aws_wafwebacl_cloudfront import WafwebaclToCloudFront
from aws_cdk import Stack
from constructs import Construct

cloudfront_to_s3 = CloudFrontToS3(self, 'test_cloudfront_s3')

# This construct can only be attached to a configured CloudFront.
WafwebaclToCloudFront(self, 'test_wafwebacl_cloudfront',
                      existing_cloud_front_web_distribution=cloudfront_to_s3.cloud_front_web_distribution
                      )
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awsconstructs.services.cloudfronts3.*;
import software.amazon.awsconstructs.services.wafwebaclcloudfront.*;

final CloudFrontToS3 cloudfrontToS3 = new CloudFrontToS3(this, "test-cloudfront-s3",
        new CloudFrontToS3Props.Builder()
                .build());

// This construct can only be attached to a configured CloudFront.
new WafwebaclToCloudFront(this, "test-wafwebacl-cloudfront", new WafwebaclToCloudFrontProps.Builder()
        .existingCloudFrontWebDistribution(cloudfrontToS3.getCloudFrontWebDistribution())
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingCloudFrontWebDistribution|[`cloudfront.Distribution`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront.Distribution.html)|The existing CloudFront instance that will be protected with the WAF web ACL. *Note that a WAF web ACL can only be added to a configured CloudFront, so this construct only accepts an existing Distribution and does not accept cloudfrontProps.*|
|existingWebaclObj?|[`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_wafv2.CfnWebACL.html)|Existing instance of a WAF web ACL, an error will occur if this and props is set.|
|webaclProps?|[`waf.CfnWebACLProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_wafv2.CfnWebACLProps.html)|Optional user-provided props to override the default props for the AWS WAF web ACL. To use a different collection of managed rule sets, specify a new rules property. Use our [`wrapManagedRuleSet(managedGroupName: string, vendorName: string, priority: number)`](../core/lib/waf-defaults.ts) function from core to create an array entry from each desired managed rule set.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|webacl|[`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_wafv2.CfnWebACL.html)|Returns an instance of the waf.CfnWebACL created by the construct.|
|cloudFrontWebDistribution|[`cloudfront.Distribution`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront.Distribution.html)|Returns an instance of cloudfront.Distribution created by the construct.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS WAF

* Deploy a WAF web ACL with 7 [AWS managed rule groups](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html).

  * AWSManagedRulesBotControlRuleSet
  * AWSManagedRulesKnownBadInputsRuleSet
  * AWSManagedRulesCommonRuleSet
  * AWSManagedRulesAnonymousIpList
  * AWSManagedRulesAmazonIpReputationList
  * AWSManagedRulesAdminProtectionRuleSet
  * AWSManagedRulesSQLiRuleSet

  *Note that the default rules can be replaced by specifying the rules property of CfnWebACLProps*
* Send metrics to Amazon CloudWatch

### Amazon CloudFront

* User provided CloudFront object is used as-is

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

import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8


class WafwebaclToCloudFront(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-cloudfront.WafwebaclToCloudFront",
):
    '''
    :summary: The WafwebaclToCloudFront class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        existing_cloud_front_web_distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
        existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
        webacl_props: typing.Any = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_cloud_front_web_distribution: The existing CloudFront instance that will be protected with the WAF web ACL. This construct changes the CloudFront distribution by directly manipulating the CloudFormation output, so this must be the Construct and cannot be changed to the Interface (IDistribution)
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :access: public
        :summary: Constructs a new instance of the WafwebaclToCloudFront class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5d8bd547f935ab6b8d3616094fcce5144f3e97e2b6bc2efff5fc3b86536057b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WafwebaclToCloudFrontProps(
            existing_cloud_front_web_distribution=existing_cloud_front_web_distribution,
            existing_webacl_obj=existing_webacl_obj,
            webacl_props=webacl_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="cloudFrontWebDistribution")
    def cloud_front_web_distribution(
        self,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "cloudFrontWebDistribution"))

    @builtins.property
    @jsii.member(jsii_name="webacl")
    def webacl(self) -> _aws_cdk_aws_wafv2_ceddda9d.CfnWebACL:
        return typing.cast(_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL, jsii.get(self, "webacl"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-cloudfront.WafwebaclToCloudFrontProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_cloud_front_web_distribution": "existingCloudFrontWebDistribution",
        "existing_webacl_obj": "existingWebaclObj",
        "webacl_props": "webaclProps",
    },
)
class WafwebaclToCloudFrontProps:
    def __init__(
        self,
        *,
        existing_cloud_front_web_distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
        existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
        webacl_props: typing.Any = None,
    ) -> None:
        '''
        :param existing_cloud_front_web_distribution: The existing CloudFront instance that will be protected with the WAF web ACL. This construct changes the CloudFront distribution by directly manipulating the CloudFormation output, so this must be the Construct and cannot be changed to the Interface (IDistribution)
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :summary: The properties for the WafwebaclToCloudFront class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40a0cf28e1b529b5efb8af1e8d3e34e9c89ef520a8810caf4b1ccce40fff2a84)
            check_type(argname="argument existing_cloud_front_web_distribution", value=existing_cloud_front_web_distribution, expected_type=type_hints["existing_cloud_front_web_distribution"])
            check_type(argname="argument existing_webacl_obj", value=existing_webacl_obj, expected_type=type_hints["existing_webacl_obj"])
            check_type(argname="argument webacl_props", value=webacl_props, expected_type=type_hints["webacl_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "existing_cloud_front_web_distribution": existing_cloud_front_web_distribution,
        }
        if existing_webacl_obj is not None:
            self._values["existing_webacl_obj"] = existing_webacl_obj
        if webacl_props is not None:
            self._values["webacl_props"] = webacl_props

    @builtins.property
    def existing_cloud_front_web_distribution(
        self,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        '''The existing CloudFront instance that will be protected with the WAF web ACL.

        This construct changes the CloudFront distribution by directly manipulating
        the CloudFormation output, so this must be the Construct and cannot be
        changed to the Interface (IDistribution)
        '''
        result = self._values.get("existing_cloud_front_web_distribution")
        assert result is not None, "Required property 'existing_cloud_front_web_distribution' is missing"
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, result)

    @builtins.property
    def existing_webacl_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL]:
        '''Existing instance of a WAF web ACL, an error will occur if this and props is set.'''
        result = self._values.get("existing_webacl_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL], result)

    @builtins.property
    def webacl_props(self) -> typing.Any:
        '''Optional user-provided props to override the default props for the AWS WAF web ACL.

        :default: - Default properties are used.
        '''
        result = self._values.get("webacl_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WafwebaclToCloudFrontProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WafwebaclToCloudFront",
    "WafwebaclToCloudFrontProps",
]

publication.publish()

def _typecheckingstub__d5d8bd547f935ab6b8d3616094fcce5144f3e97e2b6bc2efff5fc3b86536057b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    existing_cloud_front_web_distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
    existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
    webacl_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40a0cf28e1b529b5efb8af1e8d3e34e9c89ef520a8810caf4b1ccce40fff2a84(
    *,
    existing_cloud_front_web_distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
    existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
    webacl_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass
