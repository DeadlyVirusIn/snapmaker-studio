from __future__ import annotations
import json
from lxml import etree


def _hardened_parser() -> etree.XMLParser:
    # Replaces defusedxml.lxml (deprecated). Blocks XXE / entity expansion /
    # network / DTD; strict parsing (no recover); no huge-tree.
    return etree.XMLParser(resolve_entities=False, no_network=True,
                           recover=False, huge_tree=False)

def load_project_settings(raw: bytes) -> dict:
    return json.loads(raw.decode("utf-8"))

def dump_project_settings(cfg: dict) -> bytes:
    # Bambu-family uses 4-space indent, keys preserved in dict insertion order.
    return (json.dumps(cfg, indent=4, ensure_ascii=False)).encode("utf-8")

def load_model_settings(raw: bytes):
    return etree.fromstring(raw, parser=_hardened_parser())   # hardened lxml parse

def dump_model_settings(elem) -> bytes:
    return etree.tostring(elem, xml_declaration=True, encoding="UTF-8")
