from typing import List
from collections import defaultdict
from expert_dollup.core.utils.path_transform import join_uuid_path
from expert_dollup.core.domains import (
    ProjectDefinitionNode,
    ProjectDefinitionNodeTree,
    ProjectDefinitionTreeNode,
)


class ProjectDefinitionTreeBuilder:
    def __init__(self):
        pass

    def build(
        self, definitions: List[ProjectDefinitionNode]
    ) -> ProjectDefinitionNodeTree:
        node_map = defaultdict(list)
        tree_depth = None
        used_paths = set()

        for definition in definitions:
            node = ProjectDefinitionTreeNode(definition=definition, children=[])
            node_map[join_uuid_path(definition.path)].append(node)

            if tree_depth is None:
                tree_depth = len(definition.path)

            if len(node.definition.path) < tree_depth:
                children_path = join_uuid_path(
                    [*node.definition.path, node.definition.id]
                )

                assert not children_path in used_paths
                used_paths.add(children_path)

                if children_path in node_map:
                    node.children = sorted(
                        node_map[children_path],
                        key=lambda child: child.definition.ordinal,
                    )
                    del node_map[children_path]

        roots = []

        for nodes in node_map.values():
            roots.extend(nodes)

        return ProjectDefinitionNodeTree(
            roots=sorted(
                roots,
                key=lambda child: child.definition.ordinal,
            )
        )
