from volsite_postgres_common.fn.json import json_fn_db
from volworld_common.api.enum.HttpStatus import HttpStatus
from volsite_postgres_common.test.api.db_fn_open_api_validation import json_fn_db_with_validation
from volworld_common.api.CA import CA
from volsite_postgres_common.test.db.TestDb import TestDb as _TestDb


class DbCT:
    def __init__(self, context, aList):
        self.aList = aList
        self.context = context

        self.TestDb = _TestDb(context.conn, True)
        self.Resp = None
        self.UrlFeatureDict = dict()
        self.UrlScenarioDict = dict()

    def act_fn(self, fn: str, json, do_commit: bool=False):
        self.Resp = json_fn_db(fn, json, self.TestDb, self.aList, do_commit=do_commit)
        return self.Resp

    def act_fn_with_validation(self, fn: str, json, do_commit: bool=False):
        self.Resp = json_fn_db_with_validation(fn, json, self.TestDb, self.aList, do_commit=do_commit)
        self.add_url_test(self.context, fn, self.Resp)
        return self.Resp

    def assert_ok_200_resp(self, resp):
        assert resp[CA.HttpStatus] == HttpStatus.Ok_200.value
        self.Resp = resp

    @staticmethod
    def add_id_to_url_test_dict(url: str, resp, url_dict: dict, id: str):
        if url not in url_dict.keys():
            url_dict[url] = dict()
        status = resp[CA.HttpStatus]
        if status not in url_dict[url].keys():
            url_dict[url][status] = list()
        if id not in url_dict[url][status]:
            url_dict[url][status].append(id)

    def add_url_test(self, context, url: str, resp: any) -> any:
        feature_name = context.feature.name
        scenario_name = context.scenario.name
        feature_id = feature_name.split("]")[0].split("[")[1]
        scenario_id = scenario_name.split("]")[0].split("[")[1]
        print(f"Running Feature: {feature_name} -> {feature_id}")
        print(f"Running Scenario: {scenario_name} -> {scenario_id}")
        self.add_id_to_url_test_dict(url, resp, self.UrlFeatureDict, feature_id)
        self.add_id_to_url_test_dict(url, resp, self.UrlScenarioDict, scenario_id)

        return resp

    @staticmethod
    def list_id_to_wiki_link(lst: list) -> str:
        links = list()
        for i in lst:
            links.append(f"[[:{i}|{i}]]")
        return ", ".join(links)

    def print_test_features(self):
        feature_dict = self.UrlFeatureDict
        for url in feature_dict.keys():
            for status in feature_dict[url].keys():
                print(f"[{url}]({status}): {self.list_id_to_wiki_link(feature_dict[url][status])}")

    def print_test_scenarios(self):
        scenario_dict = self.UrlScenarioDict
        for url in scenario_dict.keys():
            for status in scenario_dict[url].keys():
                print(f"[{url}]({status}): {self.list_id_to_wiki_link(scenario_dict[url][status])}")