from lxml import etree, objectify
from copy import deepcopy
from tclogger import dict_get, dict_set, str_to_ts


class ElementCleaner:
    def remove_namespaces(self, element: etree._Element) -> etree._Element:
        for ele in element.getiterator():
            ele.tag = etree.QName(ele).localname
        return element

    def remove_annotations(self, element: etree._Element) -> etree._Element:
        objectify.deannotate(element, cleanup_namespaces=True)
        return element

    def clean(self, element: etree._Element) -> etree._Element:
        element = self.remove_namespaces(element)
        element = self.remove_annotations(element)
        return element


class ElementToDictConverter:
    """
    Wiki page XML format:
      * https://meta.wikimedia.org/wiki/Page_metadata

    Data dumps/Dump format - Meta
      * https://meta.wikimedia.org/wiki/Data_dumps/Dump_format
    """

    def __init__(self):
        self.cleaner = ElementCleaner()
        self.int_fields = [
            *["id", "ns", "revision.id", "revision.origin"],
            *["revision.parentid", "revision.contributor.id"],
        ]
        self.time_fields = ["revision.timestamp"]

    def to_dict(self, element: etree._Element) -> dict:
        res = {}
        if len(element) == 0:
            return element.text
        for child in element:
            res[child.tag] = self.convert(child)
            child.clear()
        return res

    def cast_types(self, doc: dict) -> dict:
        for field in self.int_fields:
            value = dict_get(doc, field)
            if value:
                dict_set(doc, field, int(value))

        for field in self.time_fields:
            value = dict_get(doc, field)
            if value:
                dict_set(doc, field, str_to_ts(value))

    def convert(self, element: etree._Element, use_root_tag: bool = False) -> dict:
        element = self.cleaner.clean(element)
        res = self.to_dict(element)
        self.cast_types(res)
        if use_root_tag:
            res = {element.tag: res}
        element.clear()
        return res
