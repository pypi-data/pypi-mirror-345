def xml_to_json(xmlFile: str, jsonFile: str):
    from xmltodict import parse
    from json import dumps

    with open(xmlFile, "r", encoding="utf-8") as f:
        json = dumps(parse(f.read()), indent=4)

    with open(jsonFile, "w", encoding="u8") as f:
        f.writelines(json)

    return "".join(json)


def csv_to_tsv(csvFile: str, tsvFile: str):
    with open(csvFile, "r", encoding="utf-8") as f:
        csv = f.readlines()

    o = []
    for i in csv:
        o.append(i.replace(", ", "\t"))

    with open(tsvFile, "w", encoding="utf-8") as f:
        f.writelines(o)
    return o


def tsv_to_csv(tsvFile: str, csvFile: str):
    with open(tsvFile, "r", encoding="utf-8") as f:
        csv = f.readlines()
    o = []

    for i in csv:
        o.append(i.replace("\t", ", "))
    with open(csvFile, "w", encoding="utf-8") as f:
        f.writelines(o)
    return o


def csv_to_json(csvFile: str, jsonFile: str):
    from json import dump

    with open(csvFile, "r", encoding="utf-8") as f:
        csv = f.read()

    with open(jsonFile, "w", encoding="utf-8") as f:
        dump(csv.split(","))


def json_to_xml(jsonFile: str, xmlFile: str):
    from json import load
    from xml.etree.ElementTree import Element, tostring

    with open(jsonFile, "r", encoding="utf-8") as f:
        json_obj = load(f)

    if isinstance(json_obj, dict):
        element = Element(json_obj.get("tag", "root"))
        for key, value in json_obj.items():
            if key == "tag":
                continue  # Skip the 'tag' key
            sub_element = Element(key)
            sub_element.text = str(value)
            element.append(sub_element)
    elif isinstance(json_obj, list):
        element = Element("root")
        for item in json_obj:
            sub_element = Element("item")
            if isinstance(item, dict):
                for k, v in item.items():
                    sub_sub_element = Element(k)
                    sub_sub_element.text = str(v)
                    sub_element.append(sub_sub_element)
            else:
                sub_element.text = str(item)
            element.append(sub_element)

    o = (
        tostring(element, encoding="utf-8", method="xml", xml_declaration=True).decode(
            "utf-8"
        )
    ).splitlines()[1]
    with open(xmlFile, "w", encoding="utf-8") as f:
        f.write(o)
    return o


def pickle_to_json(pickleFile: str, jsonFile: str):
    from json import dump
    from pickle import load

    with open(pickleFile, "rb", encoding="utf-8") as f1, open(
        jsonFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2)


def json_to_pickle(jsonFile: str, pickleFile: str):
    from pickle import dump
    from json import load

    with open(pickleFile, "wb", encoding="utf-8") as f2, open(
        jsonFile, "r", encoding="utf-8"
    ) as f1:
        dump(load(f1), f2)


def yaml_to_json(yamlFile: str, jsonFile: str):
    from yaml import load
    from json import dump

    with open(yamlFile, "r", encoding="utf-8") as f1, open(
        jsonFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2)


def json_to_yaml(jsonFile: str, yamlFile: str):
    from json import load
    from yaml import dump

    with open(jsonFile, "r", encoding="utf-8") as f1, open(
        yamlFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2, allow_unicode=True)


def toml_to_json(tomlFile: str, jsonFile: str):
    from toml import load
    from json import dump

    with open(tomlFile, "r", encoding="utf-8") as f1, open(
        jsonFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2)


def json_to_toml(jsonFile: str, tomlFile: str):
    from json import load
    from toml import dump

    with open(jsonFile, "r", encoding="utf-8") as f1, open(
        tomlFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2, allow_unicode=True)


def xml_to_jsons(xml: str):
    from xmltodict import parse
    from json import dumps

    json = dumps(parse(xml), indent=4)

    return "".join(json)


def csv_to_tsvs(csv: str):
    o = []

    for i in csv:
        o.append(i.replace(", ", "\t"))

    return o


def tsv_to_csvs(tsv: str):
    o = []

    for i in tsv:
        o.append(i.replace("\t", ", "))

    return o


def csv_to_jsons(csv: str):
    return "".join(csv.split(","))


def json_to_xmls(json: str):
    from json import loads
    from xml.etree.ElementTree import Element, tostring

    json_obj = loads(json)

    if isinstance(json_obj, dict):
        element = Element(json_obj.get("tag", "root"))
        for key, value in json_obj.items():
            if key == "tag":
                continue  # Skip the 'tag' key
            sub_element = Element(key)
            sub_element.text = str(value)
            element.append(sub_element)
    elif isinstance(json_obj, list):
        element = Element("root")
        for item in json_obj:
            sub_element = Element("item")
            if isinstance(item, dict):
                for k, v in item.items():
                    sub_sub_element = Element(k)
                    sub_sub_element.text = str(v)
                    sub_element.append(sub_sub_element)
            else:
                sub_element.text = str(item)
            element.append(sub_element)

    o = (
        tostring(element, encoding="utf-8", method="xml", xml_declaration=True).decode(
            "utf-8"
        )
    ).splitlines()[1]

    return o


def yaml_to_jsons(yaml: str):
    from yaml import load
    from json import dumps
    from os import remove

    with open("convert_cache", "w", encoding="utf-8") as f:
        f.write(yaml)

    with open("convert_cache", "r", encoding="utf-8") as f:
        return dumps(load(f))

    remove("convert_cache")


def json_to_yamls(json: str):
    from json import load
    from yaml import dump
    from os import remove

    with open("convert_cache", "w", encoding="utf-8") as f:
        f.write(json)

    with open("convert_cache", "r", encoding="utf-8") as f:
        return dump(load(f))

    remove("convert_cache")


def toml_to_jsons(toml: str):
    from toml import load
    from json import dumps
    from os import remove

    with open("convert_cache", "w", encoding="utf-8") as f:
        f.write(toml)

    with open("convert_cache", "r", encoding="utf-8") as f:
        return dumps(load(f))

    remove("convert_cache")


def json_to_tomls(jsonFile: str, tomlFile):
    from json import load
    from toml import dump

    with open(jsonFile, "r", encoding="utf-8") as f1, open(
        tomlFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2, allow_unicode=True)


def json_to_tomls(toml: str):
    from json import load
    from toml import dumps
    from os import remove

    with open("convert_cache", "w", encoding="utf-8") as f:
        f.write(toml)

    with open("convert_cache", "r", encoding="utf-8") as f:
        return dumps(load(f))

    remove("convert_cache")
