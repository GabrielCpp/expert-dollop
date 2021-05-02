from typing import List, Dict
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.utils.path_transform import join_uuid_path
from expert_dollup.core.domains import (
    ProjectNodeMeta,
    ProjectNode,
    ProjectNodeTree,
    ProjectNodeTreeNode,
    ProjectNodeTreeTypeNode,
)


class ProjectTreeBuilder:
    def __init__(self):
        pass

    def build(
        self, nodes: List[ProjectNode], metas: List[ProjectNodeMeta]
    ) -> ProjectNodeTree:
        tree_depth = None
        tree_node_map = defaultdict(list)
        meta_map = {meta.type_id: meta for meta in metas}

        for node in nodes:
            tree_node = ProjectNodeTreeNode(node=node, children=[])
            tree_node_map[join_uuid_path(node.path)].append(tree_node)

            if tree_depth is None:
                tree_depth = len(node.path)

            if len(node.path) < tree_depth:
                children_path = join_uuid_path(node.subpath)

                if children_path in tree_node_map:
                    tree_nodes = tree_node_map[children_path]
                    node.children = self._build_tree_node_list_by_type(
                        tree_nodes, meta_map
                    )
                    del node_map[children_path]

        roots = []

        for nodes in tree_node_map.values():
            roots.extend(nodes)

        return ProjectNodeTree(
            roots=self._build_tree_node_list_by_type(roots, meta_map)
        )

    def _build_tree_node_list_by_type(
        self,
        tree_nodes: List[ProjectNodeTreeNode],
        meta_map: Dict[UUID, ProjectNodeMeta],
    ) -> List[ProjectNodeTreeTypeNode]:
        tree_node_by_type = {}

        for tree_node in tree_nodes:
            type_id = tree_node.node.type_id

            if type_id in tree_node_by_type:
                tree_node_by_type[type_id].nodes.append(tree_node)
            else:
                meta = meta_map[type_id]
                tree_node_by_type[type_id] = ProjectNodeTreeTypeNode(
                    definition=meta.definition,
                    state=meta.state,
                    nodes=[tree_node],
                )

        return list(tree_node_by_type.values())