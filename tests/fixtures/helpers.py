from typing import List, Union, Generator
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *


def walk_tree(
    tree: ProjectDefinitionNodeTreeDto,
) -> Generator[ProjectDefinitionNodeDto, None, None]:
    def walk_node(
        nodes: List[ProjectDefinitionTreeNodeDto], path_trace: List[int]
    ) -> Generator[ProjectDefinitionNodeDto, None, None]:
        for index, node in enumerate(nodes):
            this_trace = [*path_trace, index]
            yield (node.definition, this_trace)
            yield from walk_node(node.children, this_trace)

    yield from walk_node(tree.roots, [])