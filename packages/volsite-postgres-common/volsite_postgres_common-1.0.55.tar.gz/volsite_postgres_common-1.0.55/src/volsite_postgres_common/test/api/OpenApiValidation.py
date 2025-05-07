import json
from typing import Final
import yaml
import os.path
import pathlib
from jsonschema.validators import RefResolver
from openapi_schema_validator import validate
from volworld_common.util.json import convert_json_by_attributes

from volsite_postgres_common.test.api.OAPI import OAPI


class OpenApiValidation:
    YamlNamePath = None
    ApiYaml = None
    ApiResolver = None
    ApiPath = None

    def __init__(self):
        if self.ApiYaml is None:
            # curr_path = pathlib.Path(__file__).parent.resolve()
            # api_yaml_path = os.path.join(curr_path, f"../../api/doc/{OpenApiValidation.YamlName}")
            print(f"Load API Yaml from [{self.YamlNamePath}]")
            assert os.path.exists(self.YamlNamePath)
            with open(self.YamlNamePath, 'r') as stream:
                self.ApiYaml = yaml.load(stream, Loader=yaml.CLoader)
            assert self.ApiYaml is not None
            self.ApiResolver = RefResolver.from_schema({
                OAPI.Components: self.ApiYaml[OAPI.Components]
            })
            self.ApiPath = self.ApiYaml[OAPI.Paths]
            self.ApiComponents = self.ApiYaml[OAPI.Components]

    def validate_POST_request(self, req, path: str, attList):
        self.validate_request(req, path, OAPI.Post, attList)

    def validate_GET_request(self, req, path: str, attList):
        self.validate_request(req, path, OAPI.Get, attList)

    def validate_request(self, req, path: str, method: str, attList):
        req_fix = convert_json_by_attributes(req, attList)
        req_fix_json = json.loads(req_fix)

        if OAPI.RequestBody not in self.ApiPath[path][method]:
            return

        request_body = self.ApiPath[path][method][OAPI.RequestBody]
        assert request_body[OAPI.Required] is True,\
            f"RequestBody of path [{path}][{method}] is NOT required.\n{request_body}."
        req_schema = request_body[OAPI.Content][OAPI.ApplicationJson][OAPI.Schema]

        # print("req_schema = ", req_schema)
        # print("tar = ", req_fix_json)
        # pprint(self.ApiComponent)

        validate(req_fix_json, req_schema, resolver=self.ApiResolver)

    def validate_POST_response(self, req, path: str, code, attList):
        self.validate_response(req, path, OAPI.Post, code, attList)

    def validate_GET_response(self, req, path: str, code, attList):
        self.validate_response(req, path, OAPI.Get, code, attList)

    def validate_response(self, res, path: str, method: str, code: str, attList):
        res_fix = convert_json_by_attributes(res, attList)
        res_fix_json = json.loads(res_fix)

        response_body = self.ApiPath[path][method][OAPI.Responses][str(code)]
        if '$ref' in response_body.keys():
            ref_val = response_body['$ref']
            if ref_val.startswith('#/paths/'):
                ref = ref_val.split('#/paths/')[1]
                ref_path = ref.split('/')[0].replace('~1', '/')
                ref_method = ref.split('/')[1]
                assert ref.split('/')[2] == 'responses'
                ref_code = ref.split('/')[3]
                response_body = self.ApiPath[ref_path][ref_method][OAPI.Responses][str(ref_code)]

            if ref_val.startswith('#/components/'):
                ref = ref_val.split('#/components/')[1]
                ref_name = ref.split('/')[0]
                ref_method = ref.split('/')[1]
                response_body = self.ApiComponents[ref_name][ref_method]

        res_schema = response_body[OAPI.Content][OAPI.ApplicationJson][OAPI.Schema]

        # print("ApiComponent = ", self.ApiComponent)
        # print("res_schema = ", res_schema)
        # print("tar = ", req_fix_json)
        # pprint(self.ApiComponent)

        validate(res_fix_json, res_schema, resolver=self.ApiResolver)

#
# path = "/inner_service___read_book_ver_structure"
# yv = YamlValidation()
# yv.validate_POST_request({"bvid": "i12345"}, path, AList)
#
# path = "/mentor_book___create_empty"
# yv = YamlValidation()
# yv.validate_POST_response({"dt__Data": {
#     "bid__BookId": "i12345",
#     "bvid__BookVersionId": "i12345"
# }}, path, 201, AList)
