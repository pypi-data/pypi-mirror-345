r'''
# aws-sns-sqs module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_sns_sqs`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-sns-sqs`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.snssqs`|

## Overview

This AWS Solutions Construct implements an Amazon SNS topic connected to an Amazon SQS queue.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { SnsToSqs, SnsToSqsProps } from "@aws-solutions-constructs/aws-sns-sqs";
import * as iam from 'aws-cdk-lib/aws-iam';

const snsToSqsStack = new SnsToSqs(this, 'SnsToSqsPattern', {});

// Grant yourself permissions to use the Customer Managed KMS Key
const policyStatement = new iam.PolicyStatement({
    actions: ["kms:Encrypt", "kms:Decrypt"],
    effect: iam.Effect.ALLOW,
    principals: [ new iam.AccountRootPrincipal() ],
    resources: [ "*" ]
});

snsToSqsStack.queueEncryptionKey?.addToResourcePolicy(policyStatement);
snsToSqsStack.topicEncryptionKey?.addToResourcePolicy(policyStatement);
```

Python

```python
from aws_solutions_constructs.aws_sns_sqs import SnsToSqs
from aws_cdk import (
    aws_iam as iam,
    Stack
)
from constructs import Construct

construct_stack = SnsToSqs(self, 'SnsToSqsPattern')

policy_statement = iam.PolicyStatement(
    actions=["kms:Encrypt", "kms:Decrypt"],
    effect=iam.Effect.ALLOW,
    principals=[iam.AccountRootPrincipal()],
    resources=["*"]
)

construct_stack.queue_encryption_key.add_to_resource_policy(policy_statement)
construct_stack.topic_encryption_key.add_to_resource_policy(policy_statement)
```

Java

```java
import software.constructs.Construct;
import java.util.List;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.services.iam.*;
import software.amazon.awsconstructs.services.snssqs.*;

final SnsToSqs constructStack = new SnsToSqs(this, "SnsToSqsPattern",
        new SnsToSqsProps.Builder()
                .build());

// Grant yourself permissions to use the Customer Managed KMS Key
final PolicyStatement policyStatement = PolicyStatement.Builder.create()
        .actions(List.of("kms:Encrypt", "kms:Decrypt"))
        .effect(Effect.ALLOW)
        .principals(List.of(new AccountRootPrincipal()))
        .resources(List.of("*"))
        .build();

constructStack.getQueueEncryptionKey().addToResourcePolicy(policyStatement);
constructStack.getTopicEncryptionKey().addToResourcePolicy(policyStatement);
```

## New Interface as of v2.58.0

As of Solutions Constructs v2.58.0, we have updated the interface of SnsToSqs. The original implementation shared a KMS customer managed key between the topic and queue. There was a single set of construct props to define this key and a single  property to access the single key. The new interface does not share a key, but uses a separate key for each resource and allows clients to control and access these keys independently.

In  CDK v2.32.0, the CDK introduced an improvement in SNS Subscriptions that narrowed the permissions to access the SQS encryption key to the specific SNS topic (it was formerly the entire SNS service). This feature created a circular reference in SnsToSqs constructs due to the shared KMS keys, but since the improvement was gated behind the feature flag `@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption`, it had no impact on existing applications. Newly generated CDK apps had the feature flag turned on by default, so would have to adjust settings to avoid the circular reference (the minimal deployment code would not work).

In addition, attempting to share the key between resources led to odd implementation choices in the construct - the implementation was highly biased towards the topic. For instance, if an existingTopic was provided but a CMK was still created to encrypt the queue that CMK was not available in the `encryptionKey` property.

Code using the original, single key props should continue to work - while that portion of the construct interface is deprecated it is not going away any time soon. Any code using any of those props, or with the new feature flag not enabled, will continue to use the old implementation. We wrote many unit tests confirming the old implementation will continue to work the same, warts and all. We do  recommend that you migrate to use the new key features to take advantage of the finer grained IAM policy for the key and more control over key behavior within the construct.

Any code that references one of the new key properties (or that enables the new feature flag) will use the new functionality.

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingTopicObj?|[`sns.Topic`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sns.Topic.html)|An optional, existing SNS topic to be used instead of the default topic. Providing both this and `topicProps` will cause an error.|
|topicProps?|[`sns.TopicProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sns.TopicProps.html)|Optional user provided properties to override the default properties for the SNS topic.|
|encryptTopicWithCmk|`boolean`|Whether to encrypt the Topic with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Topic is encrypted with an Amazon managed KMS key. For a completely unencrypted Topic (not recommended), create the Topic separately from the construct and pass it in using the existingTopicObject.|
|topicEncryptionKeyProps|[`kms.KeyProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html#construct-props)|An optional subset of key properties to override the default properties used by constructs (`enableKeyRotation: true`). These properties will be used in constructing the CMK used to encrypt the SNS topic.|
|existingTopicEncryptionKey|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html)|An optional CMK that will be used by the construct to encrypt the new SNS Topic.|
|existingQueueObj?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sqs.Queue.html)|An optional, existing SQS queue to be used instead of the default queue. Providing both this and `queueProps` will cause an error.|
|queueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sqs.QueueProps.html)|Optional user provided properties to override the default properties for the SQS queue.|
|encryptQueueWithCmk|`boolean`|Whether to encrypt the Queue with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Queue is encrypted with an Amazon managed KMS key. For a completely unencrypted Queue (not recommended), create the Queue separately from the construct and pass it in using the existingQueueObject. Since SNS subscriptions do not currently support SQS queues with AWS managed encryption keys, setting this to false will always result in an error from the underlying CDK - we have still included this property for consistency with topics and to be ready if the services one day support this functionality.|
|queueEncryptionKeyProps|[`kms.KeyProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html#construct-props)|An optional subset of key properties to override the default properties used by constructs (`enableKeyRotation: true`). These properties will be used in constructing the CMK used to encrypt the SQS queue.|
|existingQueueEncryptionKey|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html)|An optional CMK that will be used by the construct to encrypt the new SQS queue.|
|deployDeadLetterQueue?|`boolean`|Whether to create a secondary queue to be used as a dead letter queue. Defaults to true.|
|deadLetterQueueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sqs.QueueProps.html)|Optional user-provided props to override the default props for the dead letter SQS queue.|
|maxReceiveCount?|`number`|The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to 15.|
|sqsSubscriptionProps?|[`subscriptions.SqsSubscriptionProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sns_subscriptions.SqsSubscriptionProps.html)|Optional user-provided props to override the default props for sqsSubscriptionProps.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|snsTopic|[`sns.Topic`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sns.Topic.html)|Returns an instance of the SNS topic created by the pattern.|
|topicEncryptionKey?|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html)|Returns the KMS key used to encrypt the topic within the construct. Note - this is only set if the construct assigns the key, if the key is passed in topicProps it will not appear here.|
|sqsQueue|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sqs.Queue.html)|Returns an instance of the SQS queue created by the pattern.|
|queueEncryptionKey?|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html)|Returns the KMS key used to encrypt the queue within the construct. Note - this is only set if the construct assigns the key, if the key is passed in topicProps it will not appear here.|
|deadLetterQueue?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sqs.Queue.html)|Returns an instance of the dead-letter SQS queue created by the pattern.|

## Deprecated Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|enableEncryptionWithCustomerManagedKey?|`boolean`|If no key is provided, this flag determines whether the queue is encrypted with a new CMK or an AWS managed key. This flag is ignored if any of the following are defined: topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps. We recommend you migrate your code to use  encryptQueueWithCmk and encryptTopicWithCmk in place of this prop value.|
|encryptionKey?|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html)|An optional, imported encryption key to encrypt the SQS Queue and SNS Topic with. We recommend you migrate your code to use  queueEncryptionKey and topicEncryptionKey in place of this prop value.|
|encryptionKeyProps?|[`kms.KeyProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html#construct-props)|Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS topic and queue with. We recommend you migrate your code to use  queueEncryptionKeyProps and topicEncryptionKeyProps in place of this prop value.|

## Deprecated Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|encryptionKey|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kms.Key.html)|Returns an instance of kms.Key used for the SQS queue, and SNS Topic.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon SNS Topic

* Configure least privilege access permissions for SNS Topic
* Enable server-side encryption for SNS Topic using Customer managed KMS Key
* Enforce encryption of data in transit

### Amazon SQS Queue

* Configure least privilege access permissions for SQS Queue
* Deploy SQS dead-letter queue for the source SQS Queue
* Enable server-side encryption for SQS Queue using Customer managed KMS Key
* Enforce encryption of data in transit

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

import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_sns_subscriptions as _aws_cdk_aws_sns_subscriptions_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-sns-sqs.ConstructKeys",
    jsii_struct_bases=[],
    name_mapping={
        "encrypt_queue_with_cmk": "encryptQueueWithCmk",
        "encrypt_topic_with_cmk": "encryptTopicWithCmk",
        "use_deprecated_interface": "useDeprecatedInterface",
        "queue_key": "queueKey",
        "single_key": "singleKey",
        "topic_key": "topicKey",
    },
)
class ConstructKeys:
    def __init__(
        self,
        *,
        encrypt_queue_with_cmk: builtins.bool,
        encrypt_topic_with_cmk: builtins.bool,
        use_deprecated_interface: builtins.bool,
        queue_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        single_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        topic_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''
        :param encrypt_queue_with_cmk: -
        :param encrypt_topic_with_cmk: -
        :param use_deprecated_interface: -
        :param queue_key: -
        :param single_key: -
        :param topic_key: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd843496d7c11ce192f30cca99ec4efd98234b21b9d8be7b83a6bc0c86fa08d4)
            check_type(argname="argument encrypt_queue_with_cmk", value=encrypt_queue_with_cmk, expected_type=type_hints["encrypt_queue_with_cmk"])
            check_type(argname="argument encrypt_topic_with_cmk", value=encrypt_topic_with_cmk, expected_type=type_hints["encrypt_topic_with_cmk"])
            check_type(argname="argument use_deprecated_interface", value=use_deprecated_interface, expected_type=type_hints["use_deprecated_interface"])
            check_type(argname="argument queue_key", value=queue_key, expected_type=type_hints["queue_key"])
            check_type(argname="argument single_key", value=single_key, expected_type=type_hints["single_key"])
            check_type(argname="argument topic_key", value=topic_key, expected_type=type_hints["topic_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "encrypt_queue_with_cmk": encrypt_queue_with_cmk,
            "encrypt_topic_with_cmk": encrypt_topic_with_cmk,
            "use_deprecated_interface": use_deprecated_interface,
        }
        if queue_key is not None:
            self._values["queue_key"] = queue_key
        if single_key is not None:
            self._values["single_key"] = single_key
        if topic_key is not None:
            self._values["topic_key"] = topic_key

    @builtins.property
    def encrypt_queue_with_cmk(self) -> builtins.bool:
        result = self._values.get("encrypt_queue_with_cmk")
        assert result is not None, "Required property 'encrypt_queue_with_cmk' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def encrypt_topic_with_cmk(self) -> builtins.bool:
        result = self._values.get("encrypt_topic_with_cmk")
        assert result is not None, "Required property 'encrypt_topic_with_cmk' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def use_deprecated_interface(self) -> builtins.bool:
        result = self._values.get("use_deprecated_interface")
        assert result is not None, "Required property 'use_deprecated_interface' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def queue_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        result = self._values.get("queue_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def single_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        result = self._values.get("single_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def topic_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        result = self._values.get("topic_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConstructKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SnsToSqs(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-sns-sqs.SnsToSqs",
):
    '''
    :summary: The SnsToSqs class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        encrypt_queue_with_cmk: typing.Optional[builtins.bool] = None,
        encrypt_topic_with_cmk: typing.Optional[builtins.bool] = None,
        existing_queue_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        sqs_subscription_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param enable_encryption_with_customer_managed_key: (deprecated) If no keys are provided, this flag determines whether both the topic and queue are encrypted with a new CMK or an AWS managed key. This flag is ignored if any of the following are defined: topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps. Default: - True if topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey, and encryptionKeyProps are all undefined.
        :param encryption_key: (deprecated) An optional, imported encryption key to encrypt the SQS Queue and SNS Topic with. We recommend you migrate your code to use queueEncryptionKey and topicEncryptionKey in place of this prop value. Default: - None
        :param encryption_key_props: (deprecated) Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS topic and queue with. We recommend you migrate your code to use queueEncryptionKeyProps and topicEncryptionKeyProps in place of this prop value. Default: - None
        :param encrypt_queue_with_cmk: Whether to encrypt the Queue with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Queue is encrypted with an Amazon managed KMS key. For a completely unencrypted Queue (not recommended), create the Queue separately from the construct and pass it in using the existingQueueObject. Since SNS subscriptions do not currently support SQS queues with AWS managed encryption keys, setting this to false will always result in an error from the underlying CDK - we have still included this property for consistency with topics and to be ready if the services one day support this functionality. Default: - false
        :param encrypt_topic_with_cmk: Whether to encrypt the Topic with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Topic is encrypted with an Amazon managed KMS key. For a completely unencrypted Topic (not recommended), create the Topic separately from the construct and pass it in using the existingTopicObject. Default: - false
        :param existing_queue_encryption_key: An optional CMK that will be used by the construct to encrypt the new SQS queue. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_topic_encryption_key: An optional CMK that will be used by the construct to encrypt the new SNS Topic. Default: - None
        :param existing_topic_obj: Existing instance of SNS topic object, providing both this and topicProps will cause an error.. Default: - Default props are used
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_encryption_key_props: An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``). These properties will be used in constructing the CMK used to encrypt the SQS queue. Default: - None
        :param queue_props: Optional user provided properties. Default: - Default props are used
        :param sqs_subscription_props: Optional user-provided props to override the default props for sqsSubscriptionProps. Default: - Default props are used.
        :param topic_encryption_key_props: An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``). These properties will be used in constructing the CMK used to encrypt the SNS topic. Default: - None
        :param topic_props: Optional user provided properties to override the default properties for the SNS topic. Default: - Default properties are used.

        :access: public
        :since: 1.62.0
        :summary: Constructs a new instance of the SnsToSqs class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3291ed1b1af48f6773aca8d36b4a14cf3f3653fd360b8fb18cb3c250a338b8b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SnsToSqsProps(
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            enable_encryption_with_customer_managed_key=enable_encryption_with_customer_managed_key,
            encryption_key=encryption_key,
            encryption_key_props=encryption_key_props,
            encrypt_queue_with_cmk=encrypt_queue_with_cmk,
            encrypt_topic_with_cmk=encrypt_topic_with_cmk,
            existing_queue_encryption_key=existing_queue_encryption_key,
            existing_queue_obj=existing_queue_obj,
            existing_topic_encryption_key=existing_topic_encryption_key,
            existing_topic_obj=existing_topic_obj,
            max_receive_count=max_receive_count,
            queue_encryption_key_props=queue_encryption_key_props,
            queue_props=queue_props,
            sqs_subscription_props=sqs_subscription_props,
            topic_encryption_key_props=topic_encryption_key_props,
            topic_props=topic_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createRequiredKeys")
    @builtins.classmethod
    def create_required_keys(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        encrypt_queue_with_cmk: typing.Optional[builtins.bool] = None,
        encrypt_topic_with_cmk: typing.Optional[builtins.bool] = None,
        existing_queue_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        sqs_subscription_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> ConstructKeys:
        '''
        :param scope: -
        :param id: -
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param enable_encryption_with_customer_managed_key: (deprecated) If no keys are provided, this flag determines whether both the topic and queue are encrypted with a new CMK or an AWS managed key. This flag is ignored if any of the following are defined: topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps. Default: - True if topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey, and encryptionKeyProps are all undefined.
        :param encryption_key: (deprecated) An optional, imported encryption key to encrypt the SQS Queue and SNS Topic with. We recommend you migrate your code to use queueEncryptionKey and topicEncryptionKey in place of this prop value. Default: - None
        :param encryption_key_props: (deprecated) Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS topic and queue with. We recommend you migrate your code to use queueEncryptionKeyProps and topicEncryptionKeyProps in place of this prop value. Default: - None
        :param encrypt_queue_with_cmk: Whether to encrypt the Queue with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Queue is encrypted with an Amazon managed KMS key. For a completely unencrypted Queue (not recommended), create the Queue separately from the construct and pass it in using the existingQueueObject. Since SNS subscriptions do not currently support SQS queues with AWS managed encryption keys, setting this to false will always result in an error from the underlying CDK - we have still included this property for consistency with topics and to be ready if the services one day support this functionality. Default: - false
        :param encrypt_topic_with_cmk: Whether to encrypt the Topic with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Topic is encrypted with an Amazon managed KMS key. For a completely unencrypted Topic (not recommended), create the Topic separately from the construct and pass it in using the existingTopicObject. Default: - false
        :param existing_queue_encryption_key: An optional CMK that will be used by the construct to encrypt the new SQS queue. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_topic_encryption_key: An optional CMK that will be used by the construct to encrypt the new SNS Topic. Default: - None
        :param existing_topic_obj: Existing instance of SNS topic object, providing both this and topicProps will cause an error.. Default: - Default props are used
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_encryption_key_props: An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``). These properties will be used in constructing the CMK used to encrypt the SQS queue. Default: - None
        :param queue_props: Optional user provided properties. Default: - Default props are used
        :param sqs_subscription_props: Optional user-provided props to override the default props for sqsSubscriptionProps. Default: - Default props are used.
        :param topic_encryption_key_props: An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``). These properties will be used in constructing the CMK used to encrypt the SNS topic. Default: - None
        :param topic_props: Optional user provided properties to override the default properties for the SNS topic. Default: - Default properties are used.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__433722370d26c8b7be4492760e0397b31d1e59ff1129ab39692146d0443e5097)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SnsToSqsProps(
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            enable_encryption_with_customer_managed_key=enable_encryption_with_customer_managed_key,
            encryption_key=encryption_key,
            encryption_key_props=encryption_key_props,
            encrypt_queue_with_cmk=encrypt_queue_with_cmk,
            encrypt_topic_with_cmk=encrypt_topic_with_cmk,
            existing_queue_encryption_key=existing_queue_encryption_key,
            existing_queue_obj=existing_queue_obj,
            existing_topic_encryption_key=existing_topic_encryption_key,
            existing_topic_obj=existing_topic_obj,
            max_receive_count=max_receive_count,
            queue_encryption_key_props=queue_encryption_key_props,
            queue_props=queue_props,
            sqs_subscription_props=sqs_subscription_props,
            topic_encryption_key_props=topic_encryption_key_props,
            topic_props=topic_props,
        )

        return typing.cast(ConstructKeys, jsii.sinvoke(cls, "createRequiredKeys", [scope, id, props]))

    @builtins.property
    @jsii.member(jsii_name="snsTopic")
    def sns_topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "snsTopic"))

    @builtins.property
    @jsii.member(jsii_name="sqsQueue")
    def sqs_queue(self) -> _aws_cdk_aws_sqs_ceddda9d.Queue:
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.Queue, jsii.get(self, "sqsQueue"))

    @builtins.property
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue]:
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue], jsii.get(self, "deadLetterQueue"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="queueEncryptionKey")
    def queue_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], jsii.get(self, "queueEncryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="topicEncryptionKey")
    def topic_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], jsii.get(self, "topicEncryptionKey"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-sns-sqs.SnsToSqsProps",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "enable_encryption_with_customer_managed_key": "enableEncryptionWithCustomerManagedKey",
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "encrypt_queue_with_cmk": "encryptQueueWithCmk",
        "encrypt_topic_with_cmk": "encryptTopicWithCmk",
        "existing_queue_encryption_key": "existingQueueEncryptionKey",
        "existing_queue_obj": "existingQueueObj",
        "existing_topic_encryption_key": "existingTopicEncryptionKey",
        "existing_topic_obj": "existingTopicObj",
        "max_receive_count": "maxReceiveCount",
        "queue_encryption_key_props": "queueEncryptionKeyProps",
        "queue_props": "queueProps",
        "sqs_subscription_props": "sqsSubscriptionProps",
        "topic_encryption_key_props": "topicEncryptionKeyProps",
        "topic_props": "topicProps",
    },
)
class SnsToSqsProps:
    def __init__(
        self,
        *,
        dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        encrypt_queue_with_cmk: typing.Optional[builtins.bool] = None,
        encrypt_topic_with_cmk: typing.Optional[builtins.bool] = None,
        existing_queue_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        sqs_subscription_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param enable_encryption_with_customer_managed_key: (deprecated) If no keys are provided, this flag determines whether both the topic and queue are encrypted with a new CMK or an AWS managed key. This flag is ignored if any of the following are defined: topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps. Default: - True if topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey, and encryptionKeyProps are all undefined.
        :param encryption_key: (deprecated) An optional, imported encryption key to encrypt the SQS Queue and SNS Topic with. We recommend you migrate your code to use queueEncryptionKey and topicEncryptionKey in place of this prop value. Default: - None
        :param encryption_key_props: (deprecated) Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS topic and queue with. We recommend you migrate your code to use queueEncryptionKeyProps and topicEncryptionKeyProps in place of this prop value. Default: - None
        :param encrypt_queue_with_cmk: Whether to encrypt the Queue with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Queue is encrypted with an Amazon managed KMS key. For a completely unencrypted Queue (not recommended), create the Queue separately from the construct and pass it in using the existingQueueObject. Since SNS subscriptions do not currently support SQS queues with AWS managed encryption keys, setting this to false will always result in an error from the underlying CDK - we have still included this property for consistency with topics and to be ready if the services one day support this functionality. Default: - false
        :param encrypt_topic_with_cmk: Whether to encrypt the Topic with a customer managed KMS key (CMK). This is the default behavior, and this property defaults to true - if it is explicitly set to false then the Topic is encrypted with an Amazon managed KMS key. For a completely unencrypted Topic (not recommended), create the Topic separately from the construct and pass it in using the existingTopicObject. Default: - false
        :param existing_queue_encryption_key: An optional CMK that will be used by the construct to encrypt the new SQS queue. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_topic_encryption_key: An optional CMK that will be used by the construct to encrypt the new SNS Topic. Default: - None
        :param existing_topic_obj: Existing instance of SNS topic object, providing both this and topicProps will cause an error.. Default: - Default props are used
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_encryption_key_props: An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``). These properties will be used in constructing the CMK used to encrypt the SQS queue. Default: - None
        :param queue_props: Optional user provided properties. Default: - Default props are used
        :param sqs_subscription_props: Optional user-provided props to override the default props for sqsSubscriptionProps. Default: - Default props are used.
        :param topic_encryption_key_props: An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``). These properties will be used in constructing the CMK used to encrypt the SNS topic. Default: - None
        :param topic_props: Optional user provided properties to override the default properties for the SNS topic. Default: - Default properties are used.

        :summary: The properties for the SnsToSqs class.
        '''
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**dead_letter_queue_props)
        if isinstance(encryption_key_props, dict):
            encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**encryption_key_props)
        if isinstance(queue_encryption_key_props, dict):
            queue_encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**queue_encryption_key_props)
        if isinstance(queue_props, dict):
            queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**queue_props)
        if isinstance(sqs_subscription_props, dict):
            sqs_subscription_props = _aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps(**sqs_subscription_props)
        if isinstance(topic_encryption_key_props, dict):
            topic_encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**topic_encryption_key_props)
        if isinstance(topic_props, dict):
            topic_props = _aws_cdk_aws_sns_ceddda9d.TopicProps(**topic_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04b2fc5aa1881c039c3849be609fd536f9d5227c268c719b81a1d9755e9182f3)
            check_type(argname="argument dead_letter_queue_props", value=dead_letter_queue_props, expected_type=type_hints["dead_letter_queue_props"])
            check_type(argname="argument deploy_dead_letter_queue", value=deploy_dead_letter_queue, expected_type=type_hints["deploy_dead_letter_queue"])
            check_type(argname="argument enable_encryption_with_customer_managed_key", value=enable_encryption_with_customer_managed_key, expected_type=type_hints["enable_encryption_with_customer_managed_key"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_key_props", value=encryption_key_props, expected_type=type_hints["encryption_key_props"])
            check_type(argname="argument encrypt_queue_with_cmk", value=encrypt_queue_with_cmk, expected_type=type_hints["encrypt_queue_with_cmk"])
            check_type(argname="argument encrypt_topic_with_cmk", value=encrypt_topic_with_cmk, expected_type=type_hints["encrypt_topic_with_cmk"])
            check_type(argname="argument existing_queue_encryption_key", value=existing_queue_encryption_key, expected_type=type_hints["existing_queue_encryption_key"])
            check_type(argname="argument existing_queue_obj", value=existing_queue_obj, expected_type=type_hints["existing_queue_obj"])
            check_type(argname="argument existing_topic_encryption_key", value=existing_topic_encryption_key, expected_type=type_hints["existing_topic_encryption_key"])
            check_type(argname="argument existing_topic_obj", value=existing_topic_obj, expected_type=type_hints["existing_topic_obj"])
            check_type(argname="argument max_receive_count", value=max_receive_count, expected_type=type_hints["max_receive_count"])
            check_type(argname="argument queue_encryption_key_props", value=queue_encryption_key_props, expected_type=type_hints["queue_encryption_key_props"])
            check_type(argname="argument queue_props", value=queue_props, expected_type=type_hints["queue_props"])
            check_type(argname="argument sqs_subscription_props", value=sqs_subscription_props, expected_type=type_hints["sqs_subscription_props"])
            check_type(argname="argument topic_encryption_key_props", value=topic_encryption_key_props, expected_type=type_hints["topic_encryption_key_props"])
            check_type(argname="argument topic_props", value=topic_props, expected_type=type_hints["topic_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if enable_encryption_with_customer_managed_key is not None:
            self._values["enable_encryption_with_customer_managed_key"] = enable_encryption_with_customer_managed_key
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if encrypt_queue_with_cmk is not None:
            self._values["encrypt_queue_with_cmk"] = encrypt_queue_with_cmk
        if encrypt_topic_with_cmk is not None:
            self._values["encrypt_topic_with_cmk"] = encrypt_topic_with_cmk
        if existing_queue_encryption_key is not None:
            self._values["existing_queue_encryption_key"] = existing_queue_encryption_key
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if existing_topic_encryption_key is not None:
            self._values["existing_topic_encryption_key"] = existing_topic_encryption_key
        if existing_topic_obj is not None:
            self._values["existing_topic_obj"] = existing_topic_obj
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if queue_encryption_key_props is not None:
            self._values["queue_encryption_key_props"] = queue_encryption_key_props
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if sqs_subscription_props is not None:
            self._values["sqs_subscription_props"] = sqs_subscription_props
        if topic_encryption_key_props is not None:
            self._values["topic_encryption_key_props"] = topic_encryption_key_props
        if topic_props is not None:
            self._values["topic_props"] = topic_props

    @builtins.property
    def dead_letter_queue_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

        :default: - true.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_encryption_with_customer_managed_key(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''(deprecated) If no keys are provided, this flag determines whether both the topic and queue are encrypted with a new CMK or an AWS managed key.

        This flag is ignored if any of the following are defined:
        topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps.

        :default: - True if topicProps.masterKey, queueProps.encryptionMasterKey, encryptionKey, and encryptionKeyProps are all undefined.

        :deprecated: Use the separate attributes for Queue and Topic encryption.

        :stability: deprecated
        '''
        result = self._values.get("enable_encryption_with_customer_managed_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''(deprecated) An optional, imported encryption key to encrypt the SQS Queue and SNS Topic with.

        We recommend
        you migrate your code to use  queueEncryptionKey and topicEncryptionKey in place of this prop value.

        :default: - None

        :deprecated: Use the separate attributes for Queue and Topic encryption.

        :stability: deprecated
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        '''(deprecated) Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS topic and queue with.

        We recommend you migrate your code to use queueEncryptionKeyProps
        and topicEncryptionKeyProps in place of this prop value.

        :default: - None

        :deprecated: Use the separate attributes for Queue and Topic encryption.

        :stability: deprecated
        '''
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def encrypt_queue_with_cmk(self) -> typing.Optional[builtins.bool]:
        '''Whether to encrypt the Queue with a customer managed KMS key (CMK).

        This is the default
        behavior, and this property defaults to true - if it is explicitly set to false then the
        Queue is encrypted with an Amazon managed KMS key. For a completely unencrypted Queue (not recommended),
        create the Queue separately from the construct and pass it in using the existingQueueObject.
        Since SNS subscriptions do not currently support SQS queues with AWS managed encryption keys,
        setting this to false will always result in an error from the underlying CDK - we have still
        included this property for consistency with topics and to be ready if the services one day support
        this functionality.

        :default: - false
        '''
        result = self._values.get("encrypt_queue_with_cmk")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encrypt_topic_with_cmk(self) -> typing.Optional[builtins.bool]:
        '''Whether to encrypt the Topic with a customer managed KMS key (CMK).

        This is the
        default behavior, and this property defaults to true - if it is explicitly set
        to false then the Topic is encrypted with an Amazon managed KMS key. For a completely unencrypted
        Topic (not recommended), create the Topic separately from the construct and pass it in using the existingTopicObject.

        :default: - false
        '''
        result = self._values.get("encrypt_topic_with_cmk")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_queue_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''An optional CMK that will be used by the construct to encrypt the new SQS queue.

        :default: - None
        '''
        result = self._values.get("existing_queue_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        '''Existing instance of SQS queue object, Providing both this and queueProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], result)

    @builtins.property
    def existing_topic_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''An optional CMK that will be used by the construct to encrypt the new SNS Topic.

        :default: - None
        '''
        result = self._values.get("existing_topic_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def existing_topic_obj(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic]:
        '''Existing instance of SNS topic object, providing both this and topicProps will cause an error..

        :default: - Default props are used
        '''
        result = self._values.get("existing_topic_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: - required field if deployDeadLetterQueue=true.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def queue_encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        '''An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``).

        These properties will be used in constructing the CMK used to encrypt the SQS queue.

        :default: - None
        '''
        result = self._values.get("queue_encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Optional user provided properties.

        :default: - Default props are used
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    @builtins.property
    def sqs_subscription_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps]:
        '''Optional user-provided props to override the default props for sqsSubscriptionProps.

        :default: - Default props are used.
        '''
        result = self._values.get("sqs_subscription_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps], result)

    @builtins.property
    def topic_encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        '''An optional subset of key properties to override the default properties used by constructs (``enableKeyRotation: true``).

        These properties will be used in constructing the CMK used to
        encrypt the SNS topic.

        :default: - None
        '''
        result = self._values.get("topic_encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def topic_props(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps]:
        '''Optional user provided properties to override the default properties for the SNS topic.

        :default: - Default properties are used.
        '''
        result = self._values.get("topic_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsToSqsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ConstructKeys",
    "SnsToSqs",
    "SnsToSqsProps",
]

publication.publish()

def _typecheckingstub__cd843496d7c11ce192f30cca99ec4efd98234b21b9d8be7b83a6bc0c86fa08d4(
    *,
    encrypt_queue_with_cmk: builtins.bool,
    encrypt_topic_with_cmk: builtins.bool,
    use_deprecated_interface: builtins.bool,
    queue_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    single_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    topic_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3291ed1b1af48f6773aca8d36b4a14cf3f3653fd360b8fb18cb3c250a338b8b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    encrypt_queue_with_cmk: typing.Optional[builtins.bool] = None,
    encrypt_topic_with_cmk: typing.Optional[builtins.bool] = None,
    existing_queue_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    queue_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    sqs_subscription_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__433722370d26c8b7be4492760e0397b31d1e59ff1129ab39692146d0443e5097(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    encrypt_queue_with_cmk: typing.Optional[builtins.bool] = None,
    encrypt_topic_with_cmk: typing.Optional[builtins.bool] = None,
    existing_queue_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    queue_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    sqs_subscription_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04b2fc5aa1881c039c3849be609fd536f9d5227c268c719b81a1d9755e9182f3(
    *,
    dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    encrypt_queue_with_cmk: typing.Optional[builtins.bool] = None,
    encrypt_topic_with_cmk: typing.Optional[builtins.bool] = None,
    existing_queue_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
    queue_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    sqs_subscription_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_subscriptions_ceddda9d.SqsSubscriptionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
