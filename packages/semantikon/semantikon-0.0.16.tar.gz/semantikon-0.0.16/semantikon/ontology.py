from typing import TypeAlias, Any
import warnings

from rdflib import Graph, Literal, RDF, RDFS, URIRef, OWL, PROV, Namespace, BNode, SH
from dataclasses import is_dataclass
from semantikon.converter import meta_to_dict, get_function_dict
from semantikon.qudt import UnitsDict
from owlrl import DeductiveClosure, OWLRL_Semantics


class SNS:
    BASE = Namespace("http://pyiron.org/ontology/")
    hasNode = BASE["hasNode"]
    hasSourceFunction = BASE["hasSourceFunction"]
    hasUnits = BASE["hasUnits"]
    inheritsPropertiesFrom = BASE["inheritsPropertiesFrom"]
    inputOf = BASE["inputOf"]
    outputOf = BASE["outputOf"]
    hasValue = BASE["hasValue"]


class NS:
    PREFIX = "semantikon_parent_prefix"
    TYPE = "semantikon_type"


ud = UnitsDict()


def _translate_has_value(
    label: URIRef,
    tag: str,
    value: Any = None,
    dtype: type | None = None,
    units: URIRef | None = None,
    parent: URIRef | None = None,
    ontology=SNS,
) -> Graph:
    tag_uri = URIRef(tag + ".value")
    triples = [(label, ontology.hasValue, tag_uri)]
    if is_dataclass(dtype):
        warnings.warn(
            "semantikon_class is experimental - triples may change in the future",
            FutureWarning,
        )
        for k, v in dtype.__dict__.items():
            if isinstance(v, type) and is_dataclass(v):
                triples.extend(
                    _translate_has_value(
                        label=label,
                        tag=_dot(tag, k),
                        value=getattr(value, k, None),
                        dtype=v,
                        parent=tag_uri,
                        ontology=ontology,
                    )
                )
        for k, v in dtype.__annotations__.items():
            metadata = meta_to_dict(v)
            triples.extend(
                _translate_has_value(
                    label=label,
                    tag=_dot(tag, k),
                    value=getattr(value, k, None),
                    dtype=metadata["dtype"],
                    units=metadata.get("units", None),
                    parent=tag_uri,
                    ontology=ontology,
                )
            )
    else:
        if parent is not None:
            triples.append((tag_uri, RDFS.subClassOf, parent))
        if value is not None:
            triples.append((tag_uri, RDF.value, Literal(value)))
        if units is not None:
            if isinstance(units, str):
                key = ud[units]
                if key is not None:
                    triples.append((tag_uri, ontology.hasUnits, key))
                else:
                    triples.append((tag_uri, ontology.hasUnits, URIRef(units)))
            else:
                triples.append((tag_uri, ontology.hasUnits, URIRef(units)))
    return triples


def _align_triples(triples):
    if isinstance(triples[0], tuple | list):
        assert all(len(t) in (2, 3) for t in triples)
        return list(triples)
    else:
        assert len(triples) in (2, 3)
        return [triples]


def _get_triples_from_restrictions(data: dict) -> list:
    triples = []
    if data.get("restrictions", None) is not None:
        triples = _restriction_to_triple(data["restrictions"])
    if data.get("triples", None) is not None:
        triples.extend(_align_triples(data["triples"]))
    return triples


_rest_type: TypeAlias = tuple[tuple[URIRef, URIRef], ...]


def _validate_restriction_format(
    restrictions: _rest_type | tuple[_rest_type] | list[_rest_type],
) -> tuple[_rest_type]:
    if not all(isinstance(r, tuple) for r in restrictions):
        raise ValueError("Restrictions must be tuples of URIRefs")
    elif all(isinstance(rr, URIRef) for r in restrictions for rr in r):
        return (restrictions,)
    elif all(isinstance(rrr, URIRef) for r in restrictions for rr in r for rrr in rr):
        return restrictions
    else:
        raise ValueError("Restrictions must be tuples of URIRefs")


def _get_restriction_type(restriction: tuple[_rest_type]) -> URIRef:
    if restriction[0][0].startswith(OWL):
        return "OWL"
    elif restriction[0][0].startswith(SH):
        return "SH"
    raise ValueError(f"Unknown restriction type {restriction}")


def _owl_restriction_to_triple(restriction: tuple[_rest_type]) -> list:
    label = BNode()
    triples = [(None, RDF.type, label), (label, RDF.type, OWL.Restriction)]
    triples.extend([(label, r[0], r[1]) for r in restriction])
    return triples


def _sh_restriction_to_triple(restrictions: tuple[_rest_type]) -> list:
    label = BNode()
    node = restrictions[0][0] + "Node"
    triples = [
        (None, RDF.type, node),
        (node, RDF.type, SH.NodeShape),
        (node, SH.targetClass, node),
        (node, SH.property, label),
    ]
    triples.extend([(label, r[0], r[1]) for r in restrictions])
    return triples


def _restriction_to_triple(
    restrictions: _rest_type | tuple[_rest_type] | list[_rest_type],
) -> list[tuple[URIRef | None, URIRef, URIRef]]:
    """
    Convert restrictions to triples

    Args:
        restrictions (tuple): tuple of restrictions

    Returns:
        (list): list of triples

    In the semantikon notation, restrictions are given in the format:

    >>> restrictions = (
    >>>     (OWL.onProperty, EX.HasSomething),
    >>>     (OWL.someValuesFrom, EX.Something)
    >>> )

    This tuple is internally converted to the triples:

    >>> (
    >>>     (EX.HasSomethingRestriction, RDF.type, OWL.Restriction),
    >>>     (EX.HasSomethingRestriction, OWL.onProperty, EX.HasSomething),
    >>>     (EX.HasSomethingRestriction, OWL.someValuesFrom, EX.Something),
    >>>     (my_object, RDFS.subClassOf, EX.HasSomethingRestriction)
    >>> )
    """
    restrictions_collection = _validate_restriction_format(restrictions)
    triples = []
    for r in restrictions_collection:
        restriction_type = _get_restriction_type(r)
        if restriction_type == "OWL":
            triples.extend(_owl_restriction_to_triple(r))
        else:
            triples.extend(_sh_restriction_to_triple(r))
    return triples


def _parse_triple(
    triples: tuple,
    ns: str | None = None,
    label: str | URIRef | None = None,
) -> tuple:
    """
    Triples given in type hints can be expressed by a tuple of 2 or 3 elements.
    If a triple contains 2 elements, the first element is assumed to be the
    predicate and the second element the object, as semantikon automatically
    adds the argument as the subject. If a triple contains 3 elements, the
    first element is assumed to be the subject, the second element the
    predicate, and the third element the object. Instead, you can also
    indicate the position of the argument by setting it to None. Furthermore,
    if the object is a string and starts with "inputs." or "outputs.", it is
    assumed to be a channel and the namespace is added automatically.
    """
    if len(triples) == 2:
        subj, pred, obj = label, triples[0], triples[1]
    elif len(triples) == 3:
        subj, pred, obj = triples
    else:
        raise ValueError("Triple must have 2 or 3 elements")
    assert pred is not None, "Predicate must not be None"

    def _set_tag(tag, ns=None, label=None):
        if tag is None:
            return label
        elif tag.startswith("inputs.") or tag.startswith("outputs."):
            assert ns is not None, "Namespace must not be None"
            return _dot(ns, tag)
        return tag

    subj = _set_tag(subj, ns, label)
    obj = _set_tag(obj, ns, label)
    return subj, pred, obj


def _inherit_properties(
    graph: Graph, triples_to_cancel: list | None = None, n_max: int = 1000, ontology=SNS
):
    update_query = (
        f"PREFIX ns: <{ontology.BASE}>",
        f"PREFIX rdfs: <{RDFS}>",
        f"PREFIX rdf: <{RDF}>",
        f"PREFIX owl: <{OWL}>",
        "",
        "INSERT {",
        "    ?subject ?p ?o .",
        "}",
        "WHERE {",
        "    ?subject ns:inheritsPropertiesFrom ?target .",
        "    ?target ?p ?o .",
        "    FILTER(?p != ns:inheritsPropertiesFrom)",
        "    FILTER(?p != rdfs:label)",
        "    FILTER(?p != rdf:value)",
        "    FILTER(?p != ns:hasValue)",
        "    FILTER(?p != rdf:type)",
        "    FILTER(?p != owl:sameAs)",
        "}",
    )
    if triples_to_cancel is None:
        triples_to_cancel = []
    n = 0
    for _ in range(n_max):
        graph.update("\n".join(update_query))
        for t in triples_to_cancel:
            if t in graph:
                graph.remove(t)
        if len(graph) == n:
            break
        n = len(graph)


def _validate_values_by_python(graph: Graph) -> list:
    missing_triples = []
    for restrictions in graph.subjects(RDF.type, OWL.Restriction):
        on_property = graph.value(restrictions, OWL.onProperty)
        some_values_from = graph.value(restrictions, OWL.someValuesFrom)
        if on_property and some_values_from:
            for cls in graph.subjects(OWL.equivalentClass, restrictions):
                for instance in graph.subjects(RDF.type, cls):
                    if not (instance, on_property, some_values_from) in graph:
                        missing_triples.append(
                            (instance, on_property, some_values_from)
                        )
    return missing_triples


def _validate_values_by_sparql(graph: Graph) -> list:
    query = """SELECT ?instance ?onProperty ?someValuesFrom WHERE {
        ?restriction a owl:Restriction ;
                     owl:onProperty ?onProperty ;
                     owl:someValuesFrom ?someValuesFrom .

        ?cls owl:equivalentClass ?restriction .
        ?instance a ?cls .

        FILTER NOT EXISTS {
            ?instance ?onProperty ?someValuesFrom .
        }
    }"""
    return list(graph.query(query))


def validate_values(
    graph: Graph, run_reasoner: bool = True, sparql: bool = True
) -> list:
    """
    Validate if all values required by restrictions are present in the graph

    Args:
        graph (rdflib.Graph): graph to be validated
        run_reasoner (bool): if True, run the reasoner
        sparql (bool): if True, validate using SPARQL, otherwise use Python

    Returns:
        (list): list of missing triples
    """
    if run_reasoner:
        DeductiveClosure(OWLRL_Semantics).expand(graph)
    if sparql:
        return _validate_values_by_sparql(graph)
    else:
        return _validate_values_by_python(graph)


def _append_missing_items(graph: Graph) -> Graph:
    """
    This function makes sure that all properties defined in the descriptions
    become valid.
    """
    for p, o in zip(
        [OWL.onProperty, OWL.someValuesFrom, OWL.allValuesFrom],
        [RDF.Property, OWL.Class, OWL.Class],
    ):
        for obj in graph.objects(None, p):
            triple = (obj, RDF.type, o)
            if triple not in graph:
                graph.add(triple)
    return graph


def _convert_to_uriref(value):
    if isinstance(value, URIRef) or isinstance(value, Literal):
        return value  # Already a URIRef
    elif isinstance(value, str):
        return URIRef(value)  # Convert string to URIRef
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


def _function_to_triples(function: callable, node_label: str, ontology=SNS) -> list:
    f_dict = get_function_dict(function)
    triples = []
    if f_dict.get("uri", None) is not None:
        triples.append((node_label, RDF.type, f_dict["uri"]))
    if f_dict.get("triples", None) is not None:
        for t in _align_triples(f_dict["triples"]):
            triples.append(_parse_triple(t, ns=node_label, label=node_label))
    triples.append((node_label, ontology.hasSourceFunction, f_dict["label"]))
    return triples


def _parse_channel(
    channel_dict: dict, channel_label: str, edge_dict: str, ontology=SNS
):
    triples = []
    if "type_hint" in channel_dict:
        channel_dict.update(meta_to_dict(channel_dict["type_hint"]))
    triples.append((channel_label, RDF.type, PROV.Entity))
    if channel_dict.get("uri", None) is not None:
        triples.append((channel_label, RDF.type, channel_dict["uri"]))
    tag = edge_dict.get(*2 * [channel_label])
    triples.extend(
        _translate_has_value(
            label=channel_label,
            tag=tag,
            value=channel_dict.get("value", None),
            dtype=channel_dict.get("dtype", None),
            units=channel_dict.get("units", None),
            ontology=ontology,
        )
    )
    if channel_dict[NS.TYPE] == "inputs":
        triples.append(
            (channel_label, ontology.inputOf, channel_label.split(".inputs.")[0])
        )
    elif channel_dict[NS.TYPE] == "outputs":
        triples.append(
            (channel_label, ontology.outputOf, channel_label.split(".outputs.")[0])
        )
    for t in _get_triples_from_restrictions(channel_dict):
        triples.append(
            _parse_triple(t, ns=channel_dict[NS.PREFIX], label=channel_label)
        )
    return triples


def _remove_us(*arg) -> str:
    s = ".".join(arg)
    return ".".join(t.split("__")[-1] for t in s.split("."))


def _get_all_edge_dict(data):
    edges = {}
    for e in data:
        if all(["inputs." in ee for ee in e]):
            edges[e[0]] = e[1]
        else:
            edges[e[1]] = e[0]
    return edges


def _order_edge_dict(data):
    for key, value in data.items():
        if value in data:
            data[key] = data[value]
    return data


def _get_full_edge_dict(data):
    edges = _get_all_edge_dict(data)
    edges = _order_edge_dict(edges)
    return edges


def _get_edge_dict(edges: list) -> dict:
    d = {_remove_us(edge[1]): _remove_us(edge[0]) for edge in edges}
    assert len(d) == len(edges), f"Duplicate keys in edge list: {edges}"
    return d


def _dot(*args):
    return ".".join([a for a in args if a is not None])


def _convert_edge_triples(inp: str, out: str, ontology=SNS) -> tuple:
    if inp.split(".")[-2] == "outputs" or out.split(".")[-2] == "inputs":
        return (inp, OWL.sameAs, out)
    return (inp, ontology.inheritsPropertiesFrom, out)


def _edges_to_triples(edges: list, ontology=SNS) -> list:
    return [_convert_edge_triples(inp, out, ontology) for inp, out in edges.items()]


def _parse_workflow(
    node_dict: dict,
    channel_dict: dict,
    edge_list: list,
    ontology=SNS,
) -> list:
    full_edge_dict = _get_full_edge_dict(edge_list)
    triples = [
        triple
        for label, content in channel_dict.items()
        for triple in _parse_channel(content, label, full_edge_dict, ontology)
    ]
    triples.extend(_edges_to_triples(_get_edge_dict(edge_list), ontology))

    for key, node in node_dict.items():
        triples.append((key, RDF.type, PROV.Activity))
        if "function" in node:
            triples.extend(_function_to_triples(node["function"], key, ontology))
        if "." in key:
            triples.append((".".join(key.split(".")[:-1]), ontology.hasNode, key))
    return triples


def _parse_cancel(wf_channels: dict) -> list:
    triples = []
    for n_label, channel_dict in wf_channels.items():
        if "cancel" not in channel_dict:
            continue
        cancel = channel_dict["cancel"]
        assert isinstance(cancel, list | tuple)
        assert len(cancel) > 0
        if not isinstance(cancel[0], list | tuple):
            cancel = [cancel]
        for c in cancel:
            triples.append(_parse_triple(c, label=n_label))
    return [tuple([_convert_to_uriref(tt) for tt in t]) for t in triples]


def get_knowledge_graph(
    wf_dict: dict,
    graph: Graph | None = None,
    inherit_properties: bool = True,
    ontology=SNS,
    append_missing_items: bool = True,
) -> Graph:
    """
    Generate RDF graph from a dictionary containing workflow information

    Args:
        wf_dict (dict): dictionary containing workflow information
        graph (rdflib.Graph): graph to be updated
        inherit_properties (bool): if True, properties are inherited

    Returns:
        (rdflib.Graph): graph containing workflow information
    """
    if graph is None:
        graph = Graph()
    node_dict, channel_dict, edge_list = serialize_data(wf_dict)
    triples = _parse_workflow(node_dict, channel_dict, edge_list, ontology=ontology)
    triples_to_cancel = _parse_cancel(channel_dict)
    for triple in triples:
        if any(t is None for t in triple):
            continue
        converted_triples = (_convert_to_uriref(t) for t in triple)
        graph.add(converted_triples)
    if inherit_properties:
        _inherit_properties(graph, triples_to_cancel, ontology=ontology)
    if append_missing_items:
        graph = _append_missing_items(graph)
    if len(list(graph.subject_objects(SNS.hasUnits))) > 0:
        graph.bind("qudt", "http://qudt.org/vocab/unit/")
    return graph


def _is_unique(tag, graph):
    return tag not in [h for g in graph.subject_objects(None, None) for h in g]


def _dataclass_to_knowledge_graph(parent, name_space, graph=None, parent_name=None):
    if graph is None:
        graph = Graph()
    for name, obj in vars(parent).items():
        if isinstance(obj, type):  # Check if it's a class
            if _is_unique(name_space[name], graph):
                if parent_name is not None:
                    graph.add(
                        (name_space[name], RDFS.subClassOf, name_space[parent_name])
                    )
                else:
                    graph.add((name_space[name], RDF.type, RDFS.Class))
            else:
                raise ValueError(f"{name} used multiple times")
            _dataclass_to_knowledge_graph(obj, name_space, graph, name)
    return graph


def dataclass_to_knowledge_graph(class_name, name_space):
    """
    Convert a dataclass to a knowledge graph

    Args:
        class_name (dataclass): dataclass to be converted
        name_space (rdflib.Namespace): namespace to be used

    Returns:
        (rdflib.Graph): knowledge graph
    """
    return _dataclass_to_knowledge_graph(
        class_name, name_space, graph=None, parent_name=class_name.__name__
    )


def serialize_data(wf_dict: dict, prefix: str | None = None) -> tuple[dict, dict, list]:
    """
    Serialize a nested workflow dictionary into a knowledge graph

    Args:
        wf_dict (dict): workflow dictionary
        prefix (str): prefix to be used for the nodes

    Returns:
        (tuple[dict, dict, list]): node_dict, channel_dict, edge_list
    """
    edge_list = []
    channel_dict = {}
    if prefix is None:
        prefix = wf_dict["label"]
    node_dict = {
        prefix: {
            key: value
            for key, value in wf_dict.items()
            if key not in ["inputs", "outputs", "nodes", "data_edges", "label"]
        }
    }
    for io_ in ["inputs", "outputs"]:
        for key, channel in wf_dict[io_].items():
            channel_label = _remove_us(prefix, io_, key)
            assert NS.PREFIX not in channel, f"{NS.PREFIX} already set"
            assert NS.TYPE not in channel, f"{NS.TYPE} already set"
            channel_dict[channel_label] = channel | {
                NS.PREFIX: prefix,
                NS.TYPE: io_,
            }
    for key, node in wf_dict.get("nodes", {}).items():
        child_node, child_channel, child_edges = serialize_data(
            node, prefix=_dot(prefix, key)
        )
        node_dict.update(child_node)
        edge_list.extend(child_edges)
        channel_dict.update(child_channel)
    for args in wf_dict.get("data_edges", []):
        edge_list.append([_remove_us(prefix, a) for a in args])
    return node_dict, channel_dict, edge_list
