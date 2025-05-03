from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from attrs import define
from cfnlint import ConfigMixIn
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template.template import Template

from awsjavakit_cfn_rules.utils.invalid_config_exception import InvalidConfigException

EXPECTED_TAGS_FIELD_NAME = "expected_tags"

CONFIG_DEFINITION = {
    EXPECTED_TAGS_FIELD_NAME: {"default": {}, "type": "list", "itemtype": "string"}
}

NON_TAGGABLE_RESOURCES = {"AWS::IAM::Policy",
                          "AWS::IAM::RolePolicy",
                          "AWS::IAM::Role",
                          "AWS::IAM::ManagedPolicy",
                          "AWS::CloudFormation::Stack",
                          "AWS::CloudWatch::Dashboard",
                          "AWS::Events::Rule",
                          "AWS::Lambda::EventInvokeConfig",
                          "AWS::Lambda::EventSourceMapping",  # sam does not add the tags in the event invoke configs
                          "AWS::Scheduler::Schedule",
                          "AWS::SNS::Subscription",
                          "AWS::SQS::QueuePolicy",
                          "AWS::Budgets::Budget",
                          "AWS::SNS::TopicInlinePolicy",
                          "AWS::S3::BucketPolicy"
                          }
TAGS_RULE_ID = "E9001"

EMPTY_DICT = {}
EMPTY_CONFIG = []


class TagsChecker(CloudFormationLintRule):

    id: str = TAGS_RULE_ID
    shortdesc: str = "Missing Tags Rule for Resources"
    description: str = "A rule for checking that all resources have the required tags"
    tags = ["tags"]
    experimental = False

    def __init__(self):
        super().__init__()
        self.config_definition = CONFIG_DEFINITION
        self.configure()

    def match(self, cfn: Template) -> list[RuleMatch]:

        tags_rule_config = TagsRuleConfig(self.config)
        tag_rules: list[TagRule] = tags_rule_config.tag_rules()
        matches = list(map(lambda tag_rule: tag_rule.validate_template(cfn), tag_rules))
        return self._flatten_(matches)

    def _flatten_(self, matches: Iterable[list[RuntimeError]]) -> list[RuleMatch]:
        output = []
        for match in matches:
            output += match
        return output


@define
class TagsRuleConfig:
    rule_config: dict[str, list[str]]

    def tag_rules(self) -> list[TagRule]:
        tags: list[str] = self._extract_tag_config_as_dict()
        return [TagRule(expected_tag=expected_tag, excluded_resource_types=[])
                for expected_tag in tags]

    def _extract_tag_config_as_dict(self):
        config = self.rule_config.get(EXPECTED_TAGS_FIELD_NAME)
        if self._is_valid_format_(config):
            return config
        if self._is_empty_(config):
            return EMPTY_CONFIG
        raise InvalidConfigException("config is not correct")

    def _is_empty_(self, config: Any) -> bool:
        return isinstance(config, dict) and not config

    def _is_valid_format_(self, config: Any) -> bool:
        return isinstance(config, list)

    def as_cfn_config(self) -> ConfigMixIn:
        return ConfigMixIn(cli_args=None, **{EXPECTED_TAGS_FIELD_NAME: self.rule_config})


@define
class TagRule:
    excluded_resource_types: list[str]
    expected_tag: str

    def validate_template(self, cfn: Template) -> list[RuleMatch]:

        resources = cfn.get_resources()
        resource_keys = resources.keys()
        taggable_resources = list(filter(lambda key: self._is_taggable_resource_(resources.get(key)), resource_keys))
        not_excluded_for_this_tag_rule = list(
            filter(lambda key: self._is_not_excluded_(resources.get(key)), taggable_resources)
        )

        check_results = map(lambda key: self._calculate_missing_tags_(resource_name=key, resource=resources.get(key)),
                            not_excluded_for_this_tag_rule)
        non_none_check_results = filter(lambda result: result is not None, check_results)
        matches = map(lambda check_result: check_result.as_rule_match(), non_none_check_results)
        return list(matches)

    def _is_taggable_resource_(self, resource: dict) -> bool:
        return self._type_of_(resource) not in NON_TAGGABLE_RESOURCES

    def _type_of_(self, resource: dict):
        return resource.get("Type")

    def _is_not_excluded_(self, resource: dict):
        return self._type_of_(resource) not in self.excluded_resource_types

    def _calculate_missing_tags_(self, resource_name: str, resource: dict) -> CheckResult | None:
        if self.expected_tag not in self._extract_resource_tags(resource):
            return CheckResult(resource=resource, missing_tag=self.expected_tag, resource_name=resource_name)
        return None

    def _extract_resource_tags(self, resource: dict) -> list[str]:
        tags: Any = resource.get("Properties", {}).get("Tags")
        if isinstance(tags, list):
            return [tag.get('Key') for tag in tags if tag is not None]
        if isinstance(tags, dict):
            tags_as_dict: dict = tags
            return list(tags_as_dict.keys())
        return []


@define
class CheckResult:
    resource: dict
    resource_name: str
    missing_tag: str

    def as_rule_match(self) -> RuleMatch:
        return RuleMatch(path=["Resources", self.resource_name],
                         message=self._construct_message_())

    def _construct_message_(self) -> str:
        return f"Resource {self.resource_name}:{self._resource_type_()} is missing required tag:{self.missing_tag}"

    def _resource_type_(self) -> str:
        return self.resource.get("Type")
