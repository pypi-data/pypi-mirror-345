import logging

import tree_sitter_json
from tree_sitter import (
    Language as TLanguage,
)
from tree_sitter import (
    Node,
    Parser,
)

from labels.parsers.collection.types import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from labels.utils.exceptions import (
    UnexpectedNodeError,
)

LOGGER = logging.getLogger(__name__)


def _handle_array_node(node: Node) -> tuple[Node, IndexedList[ParsedValue]]:
    data: IndexedList[ParsedValue] = IndexedList(node)
    for child in node.children:
        if child.type not in ("[", "]", ","):
            try:
                value_node, value = handle_json_node(child)
                data.append((value, value_node))
            except UnexpectedNodeError:
                LOGGER.exception(
                    "Unexpected node type encountered while handling array node: %s",
                    child.type,
                    extra={
                        "extra": {
                            "node_type": child.type,
                        },
                    },
                )
                continue
    return node, data


def _handle_object_node(node: Node) -> tuple[Node, IndexedDict[str, ParsedValue]]:
    data: IndexedDict[str, ParsedValue] = IndexedDict(node)
    for child in node.children:
        if child.type == "pair":
            key_n, _, value_n = child.children
            if not key_n.text:
                continue
            key = key_n.text[1:-1].decode("utf-8")
            try:
                value_node, value_value = handle_json_node(value_n)
                data[(key, key_n)] = (value_value, value_node)
            except UnexpectedNodeError:
                LOGGER.exception(
                    "Unexpected node type encountered while handling object node: %s",
                    child.type,
                    extra={
                        "extra": {
                            "node_type": child.type,
                        },
                    },
                )
                continue
    return node, data


def handle_json_node(node: Node) -> tuple[Node, ParsedValue]:
    value: tuple[Node, ParsedValue]
    match node.type:
        case "array":
            value = _handle_array_node(node)
        case "object":
            value = _handle_object_node(node)
        case "string":
            node_value = node.text[1:-1].decode("utf-8") if node.text else ""
            value = node, node_value
        case "number":
            node_value = node.text.decode("utf-8") if node.text else "0"
            try:
                value = node, int(node_value)
            except ValueError:
                value = node, float(node_value)
        case "true":
            value = node, True
        case "false":
            value = node, False
        case "null":
            value = node, None
        case _:
            raise UnexpectedNodeError(node)
    return value


def parse_json_with_tree_sitter(
    json: str,
) -> IndexedDict[str, ParsedValue] | IndexedList[ParsedValue]:
    parser_language = TLanguage(tree_sitter_json.language())
    parser = Parser(parser_language)
    result = parser.parse(json.encode("utf-8"))
    value: ParsedValue = IndexedDict()
    for child in result.root_node.children:
        try:
            _, value = handle_json_node(child)
        except UnexpectedNodeError:
            LOGGER.exception(
                "Unexpected node type encountered: %s",
                child.type,
                extra={
                    "extra": {
                        "node_type": child.type,
                        "json": json,
                    },
                },
            )
            continue
    if value is None or not isinstance(value, IndexedDict | IndexedList):
        LOGGER.warning(
            "JSON parsing failed.",
            extra={"extra": {"json": json}},
        )
        return IndexedDict()
    return value
