import json
ResourcesPool = "../ResourcesPool/"
apis = open(ResourcesPool + "Apis.json", "r", encoding="utf-8").read()
apis = json.loads(apis)

argsMap = {}

for key, v in apis.items():
    if isinstance(apis[key], dict) and v:
        for k_, v_ in apis[key].items():
            if isinstance(v_, dict) and 'body' in v_.keys():
                for _k, _v in v_['body'].items():
                    if _k not in argsMap and _v == "Fuzzable":
                        argsMap[_k] = "Fuzzable"
                        apis[key][k_]['body'][_k] = "Fuzzable"
                    elif _k in argsMap and argsMap[_k] != "Fuzzable" and _v == "Fuzzable":
                        argsMap[_k] = "Fuzzable"
                        apis[key][k_]['body'][_k] = "Fuzzable"
                    # if _v != "Fuzzable":
                    #     apis[key][k_]['body'][_k] = argsMap[_k]

for key, v in apis.items():
    if isinstance(apis[key], dict) and v:
        for k_, v_ in apis[key].items():
            if isinstance(v_, dict) and 'body' in v_.keys():
                for _k, _v in v_['body'].items():
                    if apis[key][k_]['body'][_k] != "Fuzzable":
                        if _k in argsMap and argsMap[_k] == "Fuzzable":
                            apis[key][k_]['body'][_k] = "Fuzzable"

# print(apis)

with open(ResourcesPool + "parsedApis.json", "w", encoding="utf-8") as f:
    json.dump(apis, f, indent=2, ensure_ascii=False)