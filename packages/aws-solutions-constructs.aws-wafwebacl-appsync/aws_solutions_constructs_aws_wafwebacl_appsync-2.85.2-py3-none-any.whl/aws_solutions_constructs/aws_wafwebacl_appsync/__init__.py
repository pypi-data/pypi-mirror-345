r'''
# aws-wafwebacl-appsync module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**: | <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span> |
| :--------------------------- | :------------------------------------------------------------------------------------------------ |

<div style="height:8px"></div>

| **Language**                                                                                   | **Package**                                               |
| :--------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| ![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python             | `aws_solutions_constructs.aws_wafwebacl_appsync`          |
| ![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript | `@aws-solutions-constructs/aws-wafwebacl-appsync`         |
| ![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java                   | `software.amazon.awsconstructs.services.wafwebaclappsync` |

## Overview

This AWS Solutions Construct implements an AWS WAF web ACL connected to an AWS AppSync API.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from "constructs";
import { Stack, StackProps } from "aws-cdk-lib";
import {
  WafwebaclToAppsyncProps,
  WafwebaclToAppsync,
} from "@aws-solutions-constructs/aws-wafwebacl-appsync";

// Use an existing AppSync GraphQL API
const existingGraphQLApi = previouslyCreatedApi;

// This construct can only be attached to a configured AWS AppSync API.
new WafwebaclToAppsync(this, "test-wafwebacl-appsync", {
  existingAppsyncApi: existingGraphQLApi,
});
```

Python

```python
from aws_solutions_constructs.aws_wafwebacl_appsync import WafwebaclToAppsyncProps, WafwebaclToAppsync
from aws_cdk import (
    aws_route53 as route53,
    Stack
)
from constructs import Construct

# Use an existing AppSync API
existingGraphQLApi = previouslyCreatedApi


# This construct can only be attached to a configured AWS AppSync API.
WafwebaclToAppsync(self, 'test_wafwebacl_appsync',
                existing_appsync_api=existingGraphQLApi
                )
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awsconstructs.services.wafwebaclappsync.*;

// Use an existing AppSync API
final existingGraphQLApi = previouslyCreatedApi


// This construct can only be attached to a configured AWS AppSync API.
new WafwebaclToAppsync(this, "test-wafwebacl-appsync", new WafwebaclToAppsyncProps.Builder()
        .existingAppsyncApi(existingGraphQLApi)
        .build());
```

## Pattern Construct Props

| **Name**           | **Type**                                                                                                          | **Description**                                                                                                                                                                                                                                                                                                                                                                   |
| :----------------- | :---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| existingAppsyncApi | [`appsync.CfnGraphQLApi`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_appsync.CfnGraphQLApi.html) | The existing Appsync CfnGraphQLApi object that will be protected with the WAF web ACL. *Note that a WAF web ACL can only be added to a configured AppSync API, so this construct only accepts an existing CfnGraphQLApi and does not accept CfnGraphQLApiProps.*                                                                                                                  |
| existingWebaclObj? | [`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_waf.CfnWebACL.html)                 | Existing instance of a WAF web ACL, an error will occur if this and props is set.                                                                                                                                                                                                                                                                                                 |
| webaclProps?       | [`waf.CfnWebACLProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_waf.CfnWebACLProps.html)       | Optional user-provided props to override the default props for the AWS WAF web ACL. To use a different collection of managed rule sets, specify a new rules property. Use our [`wrapManagedRuleSet(managedGroupName: string, vendorName: string, priority: number)`](../core/lib/waf-defaults.ts) function from core to create an array entry from each desired managed rule set. |

## Pattern Properties

| **Name**   | **Type**                                                                                                          | **Description**                                                    |
| :--------- | :---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| webacl     | [`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_waf.CfnWebACL.html)                 | Returns an instance of the waf.CfnWebACL created by the construct. |
| appsyncApi | [`appsync.CfnGraphQLApi`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_appsync.CfnGraphQLApi.html) | Returns an instance of the CfnGraphQLApi used by the pattern.      |

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

### AppSync API

* User provided AppSync graphql API object is used as-is

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

import aws_cdk.aws_appsync as _aws_cdk_aws_appsync_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8


class WafwebaclToAppsync(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-appsync.WafwebaclToAppsync",
):
    '''
    :summary: The WafwebaclToAppsync class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        existing_appsync_api: _aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi,
        existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
        webacl_props: typing.Any = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_appsync_api: The existing Appsync API that will be protected with the WAF web ACL.
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :access: public
        :summary: Constructs a new instance of the WafwebaclToAppsync class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab36bcf291466e1edd94e156a9741b78f8c66d4f700d9207b00d2648e6c8a635)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WafwebaclToAppsyncProps(
            existing_appsync_api=existing_appsync_api,
            existing_webacl_obj=existing_webacl_obj,
            webacl_props=webacl_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="appsyncApi")
    def appsync_api(self) -> _aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi:
        return typing.cast(_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi, jsii.get(self, "appsyncApi"))

    @builtins.property
    @jsii.member(jsii_name="webacl")
    def webacl(self) -> _aws_cdk_aws_wafv2_ceddda9d.CfnWebACL:
        return typing.cast(_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL, jsii.get(self, "webacl"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-appsync.WafwebaclToAppsyncProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_appsync_api": "existingAppsyncApi",
        "existing_webacl_obj": "existingWebaclObj",
        "webacl_props": "webaclProps",
    },
)
class WafwebaclToAppsyncProps:
    def __init__(
        self,
        *,
        existing_appsync_api: _aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi,
        existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
        webacl_props: typing.Any = None,
    ) -> None:
        '''
        :param existing_appsync_api: The existing Appsync API that will be protected with the WAF web ACL.
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :summary: The properties for the WafwebaclToAppsync class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd85c5128842da8bb7da69d48ffe2dc361a2ce2becdad52b1c5296c4fefff6f)
            check_type(argname="argument existing_appsync_api", value=existing_appsync_api, expected_type=type_hints["existing_appsync_api"])
            check_type(argname="argument existing_webacl_obj", value=existing_webacl_obj, expected_type=type_hints["existing_webacl_obj"])
            check_type(argname="argument webacl_props", value=webacl_props, expected_type=type_hints["webacl_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "existing_appsync_api": existing_appsync_api,
        }
        if existing_webacl_obj is not None:
            self._values["existing_webacl_obj"] = existing_webacl_obj
        if webacl_props is not None:
            self._values["webacl_props"] = webacl_props

    @builtins.property
    def existing_appsync_api(self) -> _aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi:
        '''The existing Appsync API that will be protected with the WAF web ACL.'''
        result = self._values.get("existing_appsync_api")
        assert result is not None, "Required property 'existing_appsync_api' is missing"
        return typing.cast(_aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi, result)

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
        return "WafwebaclToAppsyncProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WafwebaclToAppsync",
    "WafwebaclToAppsyncProps",
]

publication.publish()

def _typecheckingstub__ab36bcf291466e1edd94e156a9741b78f8c66d4f700d9207b00d2648e6c8a635(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    existing_appsync_api: _aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi,
    existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
    webacl_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd85c5128842da8bb7da69d48ffe2dc361a2ce2becdad52b1c5296c4fefff6f(
    *,
    existing_appsync_api: _aws_cdk_aws_appsync_ceddda9d.CfnGraphQLApi,
    existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
    webacl_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass
