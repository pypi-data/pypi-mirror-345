from networkx import Graph, connected_components

from ..memoryset import LabeledMemoryset


def group_potential_duplicates(memoryset: LabeledMemoryset) -> list[list[str]]:
    """
    Calculate the potential duplicate groups for a given memoryset.
    """

    graph = Graph()
    query = memoryset.query(filters=[("metrics.has_potential_duplicates", "==", True)])

    # First add all nodes that have potential duplicates
    for mem in query:
        graph.add_node(mem.memory_id)
        potential_duplicates = mem.metrics.get("potential_duplicate_memory_ids")
        if potential_duplicates is not None:
            for duplicate_id in potential_duplicates:
                # Add the duplicate node if it doesn't exist
                graph.add_node(duplicate_id)
                graph.add_edge(mem.memory_id, duplicate_id)

    group_list = []
    for component in connected_components(graph):
        subgroup = []
        for mem_id in component:
            subgroup.append(mem_id)
        group_list.append(subgroup)

    return group_list
