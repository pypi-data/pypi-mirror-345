from __future__ import annotations

from typing import Optional, Sequence, TypedDict

import numpy as np
from gpp.config import IDENT_PROPS
from sm.dataset import Example, FullTable
from sm.misc.prelude import IntegerEncoder
from sm.namespaces.prelude import KnowledgeGraphNamespace
from smml.data_model_helper import SingleNumpyArray


class GetSampleLabelOutput(TypedDict):
    sample_id: SingleNumpyArray
    table_id: SingleNumpyArray
    column_index: SingleNumpyArray
    column_name: SingleNumpyArray
    column_type: SingleNumpyArray
    original_column_type: SingleNumpyArray


def get_sample_label(
    exs: Sequence[Example[FullTable]],
    kgns: KnowledgeGraphNamespace,
    ignore_no_type_column: bool = True,
) -> GetSampleLabelOutput:
    sample_id = []
    table_id = []
    column_index = []
    column_name = []
    column_type = IntegerEncoder()

    for ex in exs:
        for col in ex.table.table.columns:
            label = set()

            for sm in ex.sms:
                if not sm.has_data_node(col.index):
                    continue
                u = sm.get_data_node(col.index)
                for t in sm.get_semantic_types_of_column(col.index):
                    if t.predicate_abs_uri in IDENT_PROPS:
                        label.add(t.class_abs_uri)

                        # also add the incoming property/qualifier
                        (inedge,) = sm.in_edges(u.id)
                        for inedge2 in sm.in_edges(inedge.source):
                            label.add(inedge2.abs_uri)
                    elif t.qualifier_abs_uri is None:
                        label.add(t.predicate_abs_uri)
                    else:
                        label.add(t.qualifier_abs_uri)

            if ignore_no_type_column and len(label) == 0:
                continue

            sample_id.append(len(sample_id))
            table_id.append(ex.table.table.table_id)
            column_index.append(col.index)
            column_name.append(col.clean_multiline_name)
            column_type.append(tuple(sorted((kgns.uri_to_id(uri) for uri in label))))

    # can't use np.array(column_type.get_decoder(), dtype=np.object_) if all elements are one item list
    # as it will create a 2D array.
    encoded_column_type = column_type.get_decoder()
    original_column_type = np.empty((len(encoded_column_type),), dtype=np.object_)
    original_column_type[:] = encoded_column_type

    return {
        "sample_id": SingleNumpyArray(np.array(sample_id)),
        "table_id": SingleNumpyArray(np.array(table_id, dtype=np.object_)),
        "column_index": SingleNumpyArray(np.array(column_index)),
        "column_name": SingleNumpyArray(np.array(column_name, dtype=np.object_)),
        "column_type": SingleNumpyArray(np.array(column_type.values)),
        "original_column_type": SingleNumpyArray(original_column_type),
    }
