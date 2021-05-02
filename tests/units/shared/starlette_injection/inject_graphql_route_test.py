from expert_dollup.shared.starlette_injection.inject_graphql_route import collapse_union


def test_collapse_union():
    node = {
        "id": "24ef7c23-48d0-4d09-95b7-3962ad65e406",
        "projectDefId": "0217b036-20da-428b-9cfc-828b2b5cb93d",
        "name": "g",
        "isCollection": True,
        "instanciateByDefault": True,
        "orderIndex": 0,
        "config": {
            "fieldDetails": {
                "kind": "COLLAPSIBLE_CONTAINER_FIELD_CONFIG",
                "collapsibleContainer": {"isCollapsible": True},
            },
            "valueValidator": None,
        },
        "defaultValue": None,
        "path": [],
    }

    node = collapse_union(
        node,
        ["config", "fieldDetails"],
        {
            "INT_FIELD_CONFIG": "int",
            "DECIMAL_FIELD_CONFIG": "decimal",
            "STRING_FIELD_CONFIG": "string",
            "BOOL_FIELD_CONFIG": "bool",
            "STATIC_CHOICE_FIELD_CONFIG": "staticChoice",
            "COLLAPSIBLE_CONTAINER_FIELD_CONFIG": "collapsibleContainer",
        },
    )

    assert node == {
        "id": "24ef7c23-48d0-4d09-95b7-3962ad65e406",
        "projectDefId": "0217b036-20da-428b-9cfc-828b2b5cb93d",
        "name": "g",
        "isCollection": True,
        "instanciateByDefault": True,
        "orderIndex": 0,
        "config": {
            "fieldDetails": {"isCollapsible": True},
            "valueValidator": None,
        },
        "defaultValue": None,
        "path": [],
    }
