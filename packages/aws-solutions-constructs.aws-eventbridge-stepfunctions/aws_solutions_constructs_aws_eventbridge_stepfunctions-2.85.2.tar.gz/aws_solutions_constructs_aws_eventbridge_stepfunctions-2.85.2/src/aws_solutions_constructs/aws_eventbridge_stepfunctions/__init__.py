r'''
# aws-eventbridge-stepfunctions module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_eventbridge_stepfunctions`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-eventbridge-stepfunctions`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.eventbridgestepfunctions`|

## Overview

This AWS Solutions Construct implements an AWS Events rule and an AWS Step Functions State Machine

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps, Duration } from 'aws-cdk-lib';
import { EventbridgeToStepfunctions, EventbridgeToStepfunctionsProps } from '@aws-solutions-constructs/aws-eventbridge-stepfunctions';
import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';
import * as events from 'aws-cdk-lib/aws-events';

const startState = new stepfunctions.Pass(this, 'StartState');

const constructProps: EventbridgeToStepfunctionsProps = {
  stateMachineProps: {
    definition: startState
  },
  eventRuleProps: {
    schedule: events.Schedule.rate(Duration.minutes(5))
  }
};

new EventbridgeToStepfunctions(this, 'test-eventbridge-stepfunctions-stack', constructProps);
```

Python

```python
from aws_solutions_constructs.aws_eventbridge_stepfunctions import EventbridgeToStepfunctions, EventbridgeToStepfunctionsProps
from aws_cdk import (
    aws_stepfunctions as stepfunctions,
    aws_events as events,
    Duration,
    Stack
)
from constructs import Construct

startState = stepfunctions.Pass(self, 'StartState')

EventbridgeToStepfunctions(self, 'test-eventbridge-stepfunctions-stack',
                            state_machine_props=stepfunctions.StateMachineProps(
                                definition=startState
                            ),
                            event_rule_props=events.RuleProps(
                                schedule=events.Schedule.rate(
                                    Duration.minutes(5))
                            ))
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.Duration;
import software.amazon.awscdk.services.events.*;
import software.amazon.awscdk.services.stepfunctions.*;
import software.amazon.awsconstructs.services.eventbridgestepfunctions.*;

final Pass startState = new Pass(this, "StartState");

new EventbridgeToStepfunctions(this,
        "test-eventbridge-stepfunctions-stack",
        new EventbridgeToStepfunctionsProps.Builder()
                .stateMachineProps(new StateMachineProps.Builder()
                        .definition(startState)
                        .build())
                .eventRuleProps(new RuleProps.Builder()
                        .schedule(Schedule.rate(Duration.minutes(5)))
                        .build())
                .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|stateMachineProps|[`sfn.StateMachineProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_stepfunctions.StateMachineProps.html)|Optional user provided props to override the default props for sfn.StateMachine|
|existingEventBusInterface?|[`events.IEventBus`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.IEventBus.html)| Optional user-provided custom EventBus for construct to use. Providing both this and `eventBusProps` results an error.|
|eventBusProps?|[`events.EventBusProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.EventBusProps.html)|Optional user-provided properties to override the default properties when creating a custom EventBus. Setting this value to `{}` will create a custom EventBus using all default properties. If neither this nor `existingEventBusInterface` is provided the construct will use the `default` EventBus. Providing both this and `existingEventBusInterface` results an error.|
|eventRuleProps|[`events.RuleProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.RuleProps.html)|User provided eventRuleProps to override the defaults|
|createCloudWatchAlarms|`boolean`|Whether to create recommended CloudWatch alarms|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|eventBus?|[`events.IEventBus`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.IEventBus.html)|Returns the instance of events.IEventBus used by the construct|
|eventsRule|[`events.Rule`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.Rule.html)|Returns an instance of events.Rule created by the construct|
|stateMachine|[`sfn.StateMachine`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_stepfunctions.StateMachine.html)|Returns an instance of sfn.StateMachine created by the construct|
|stateMachineLogGroup|[`logs.ILogGroup`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_logs.ILogGroup.html)|Returns an instance of the ILogGroup created by the construct for StateMachine|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudwatch.Alarm.html)|Returns a list of cloudwatch.Alarm created by the construct|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon CloudWatch Events Rule

* Grant least privilege permissions to CloudWatch Events to trigger the Lambda Function

### AWS Step Function

* Enable CloudWatch logging for API Gateway
* Deploy best practices CloudWatch Alarms for the Step Function

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

import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import constructs as _constructs_77d1e7e8


class EventbridgeToStepfunctions(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-eventbridge-stepfunctions.EventbridgeToStepfunctions",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        event_rule_props: typing.Union[_aws_cdk_aws_events_ceddda9d.RuleProps, typing.Dict[builtins.str, typing.Any]],
        state_machine_props: typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps, typing.Dict[builtins.str, typing.Any]],
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_event_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param event_rule_props: User provided eventRuleProps to override the defaults. Default: - None
        :param state_machine_props: User provided StateMachineProps to override the defaults. Default: - None
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param event_bus_props: A new custom EventBus is created with provided props. Default: - None
        :param existing_event_bus_interface: Existing instance of a custom EventBus. Default: - None
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :access: public
        :summary: Constructs a new instance of the EventbridgeToStepfunctions class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11fd8cf8c2aa86550aadcaf0eb827e799d64f4cb5b9b5a38849b89c0caa910dd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EventbridgeToStepfunctionsProps(
            event_rule_props=event_rule_props,
            state_machine_props=state_machine_props,
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            event_bus_props=event_bus_props,
            existing_event_bus_interface=existing_event_bus_interface,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="eventsRule")
    def events_rule(self) -> _aws_cdk_aws_events_ceddda9d.Rule:
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.get(self, "eventsRule"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineLogGroup")
    def state_machine_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "stateMachineLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm]], jsii.get(self, "cloudwatchAlarms"))

    @builtins.property
    @jsii.member(jsii_name="eventBus")
    def event_bus(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], jsii.get(self, "eventBus"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-eventbridge-stepfunctions.EventbridgeToStepfunctionsProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_rule_props": "eventRuleProps",
        "state_machine_props": "stateMachineProps",
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "event_bus_props": "eventBusProps",
        "existing_event_bus_interface": "existingEventBusInterface",
        "log_group_props": "logGroupProps",
    },
)
class EventbridgeToStepfunctionsProps:
    def __init__(
        self,
        *,
        event_rule_props: typing.Union[_aws_cdk_aws_events_ceddda9d.RuleProps, typing.Dict[builtins.str, typing.Any]],
        state_machine_props: typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps, typing.Dict[builtins.str, typing.Any]],
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_event_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param event_rule_props: User provided eventRuleProps to override the defaults. Default: - None
        :param state_machine_props: User provided StateMachineProps to override the defaults. Default: - None
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param event_bus_props: A new custom EventBus is created with provided props. Default: - None
        :param existing_event_bus_interface: Existing instance of a custom EventBus. Default: - None
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :summary: The properties for the EventbridgeToStepfunctions Construct
        '''
        if isinstance(event_rule_props, dict):
            event_rule_props = _aws_cdk_aws_events_ceddda9d.RuleProps(**event_rule_props)
        if isinstance(state_machine_props, dict):
            state_machine_props = _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps(**state_machine_props)
        if isinstance(event_bus_props, dict):
            event_bus_props = _aws_cdk_aws_events_ceddda9d.EventBusProps(**event_bus_props)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9254281d961668e5283454dbaeefa487e00b7213373a3fd22fb4b8bc4b9fbd)
            check_type(argname="argument event_rule_props", value=event_rule_props, expected_type=type_hints["event_rule_props"])
            check_type(argname="argument state_machine_props", value=state_machine_props, expected_type=type_hints["state_machine_props"])
            check_type(argname="argument create_cloud_watch_alarms", value=create_cloud_watch_alarms, expected_type=type_hints["create_cloud_watch_alarms"])
            check_type(argname="argument event_bus_props", value=event_bus_props, expected_type=type_hints["event_bus_props"])
            check_type(argname="argument existing_event_bus_interface", value=existing_event_bus_interface, expected_type=type_hints["existing_event_bus_interface"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_rule_props": event_rule_props,
            "state_machine_props": state_machine_props,
        }
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if event_bus_props is not None:
            self._values["event_bus_props"] = event_bus_props
        if existing_event_bus_interface is not None:
            self._values["existing_event_bus_interface"] = existing_event_bus_interface
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def event_rule_props(self) -> _aws_cdk_aws_events_ceddda9d.RuleProps:
        '''User provided eventRuleProps to override the defaults.

        :default: - None
        '''
        result = self._values.get("event_rule_props")
        assert result is not None, "Required property 'event_rule_props' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.RuleProps, result)

    @builtins.property
    def state_machine_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps:
        '''User provided StateMachineProps to override the defaults.

        :default: - None
        '''
        result = self._values.get("state_machine_props")
        assert result is not None, "Required property 'state_machine_props' is missing"
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps, result)

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBusProps]:
        '''A new custom EventBus is created with provided props.

        :default: - None
        '''
        result = self._values.get("event_bus_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBusProps], result)

    @builtins.property
    def existing_event_bus_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''Existing instance of a custom EventBus.

        :default: - None
        '''
        result = self._values.get("existing_event_bus_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

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
        return "EventbridgeToStepfunctionsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EventbridgeToStepfunctions",
    "EventbridgeToStepfunctionsProps",
]

publication.publish()

def _typecheckingstub__11fd8cf8c2aa86550aadcaf0eb827e799d64f4cb5b9b5a38849b89c0caa910dd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    event_rule_props: typing.Union[_aws_cdk_aws_events_ceddda9d.RuleProps, typing.Dict[builtins.str, typing.Any]],
    state_machine_props: typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps, typing.Dict[builtins.str, typing.Any]],
    create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
    event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_event_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9254281d961668e5283454dbaeefa487e00b7213373a3fd22fb4b8bc4b9fbd(
    *,
    event_rule_props: typing.Union[_aws_cdk_aws_events_ceddda9d.RuleProps, typing.Dict[builtins.str, typing.Any]],
    state_machine_props: typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps, typing.Dict[builtins.str, typing.Any]],
    create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
    event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_event_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
