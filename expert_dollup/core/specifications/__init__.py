from expert_dollup.shared.database_services import DatabaseContext


@dataclass
class ProjectNodeAggregate(ProjectNode):
    project: ProjectDetails
    type_path_nodes: List[ProjectDefinitionNode]
    type_node: ProjectDefinitionNode
    path_nodes: List[ProjectNode]


def create_project_node_aggregate(
    node, loader: AggregateLoader
) -> ProjectNodeAggregate:

    return ProjectNodeAggregate()


def validate_nodes(loader, nodes):
    node_aggregate = create_project_node_aggregate(loader, nodes)
    project_definition_id = node_aggregate.project.project_definition_id
    project_id = node_aggregate.project_id
    node_spec = ChecksSpec(
        [
            CheckForEachSpec(
                lambda i: f"type_path.{i}",
                "nodes.must_share_same_project_definition_id",
                lambda aggregate: aggregate.type_path_nodes,
                lambda node: node.project_definition_id == project_definition_id,
            ),
            CheckSpec(
                lambda i: f"type_id.{i}",
                "nodes.must_share_same_project_definition_id",
                lambda node: node.type_node.project_definition_id
                == project_definition_id,
            ),
            CheckForEachSpec(
                lambda i: f"path.{i}",
                "nodes.must_share_same_project_id",
                lambda aggregate: aggregate.path_nodes,
                lambda node: node.project_id == project_id,
            ),
        ]
    )
