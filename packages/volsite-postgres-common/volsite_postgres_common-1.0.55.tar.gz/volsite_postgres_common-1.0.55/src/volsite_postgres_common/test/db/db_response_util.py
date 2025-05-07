from volworld_common.api.CA import CA


def response_to_dict(resp_json) -> dict:
    resp_data = None
    resp_error = None

    if CA.___Error___ in resp_json.keys():
        resp_error = resp_json[CA.___Error___]
    else:
        resp_data = resp_json[CA.Data]

    return {
            CA.HttpStatus: resp_json[CA.HttpStatus],
            CA.Data: resp_data,
            CA.___Error___: resp_error,
            CA.Response: resp_json
        }
