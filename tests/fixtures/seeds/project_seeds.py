from decimal import Decimal
from ..factories.project_instance_factory import (
    ProjectSeed,
    DefNodeSeed,
    NodeSeed,
    FormulaSeed,
)


def make_base_project_seed():
    project_seed = ProjectSeed(
        {
            "rootA": DefNodeSeed(
                {
                    "1": NodeSeed(
                        formulas={
                            "formulaA": FormulaSeed(
                                expression="fieldB*fieldA",
                                formula_dependencies=[],
                                node_dependencies=["fieldB", "fieldA"],
                                calculation_details="<fieldB, 2> * sum(<fieldA, 12>)",
                                result=Decimal(24),
                            ),
                            "formulaB": FormulaSeed(
                                expression="fieldB*sectionA_formula",
                                formula_dependencies=["sectionA_formula"],
                                node_dependencies=["fieldB"],
                            ),
                        }
                    )
                }
            ),
            "rootB": DefNodeSeed(),
            "subSectionA": DefNodeSeed({"1": NodeSeed(parent="rootA-1")}),
            "formA": DefNodeSeed({"1": NodeSeed(parent="subSectionA-1")}),
            "sectionA": DefNodeSeed(
                {
                    "1": NodeSeed(
                        parent="formA-1",
                        formulas={
                            "sectionA_formula": FormulaSeed(
                                expression="fieldA-2",
                                formula_dependencies=[],
                                node_dependencies=["fieldA"],
                            ),
                        },
                    ),
                    "2": NodeSeed(
                        parent="formA-1",
                        formulas={
                            "sectionA_formula": FormulaSeed(
                                expression="fieldA-2",
                                formula_dependencies=[],
                                node_dependencies=["fieldA"],
                            ),
                        },
                    ),
                    "3": NodeSeed(
                        parent="formA-1",
                        formulas={
                            "sectionA_formula": FormulaSeed(
                                expression="fieldA-2",
                                formula_dependencies=[],
                                node_dependencies=["fieldA"],
                            ),
                        },
                    ),
                }
            ),
            "fieldA": DefNodeSeed(
                {
                    "1": NodeSeed(
                        parent="sectionA-1",
                        value=Decimal(5),
                    ),
                    "2": NodeSeed(
                        parent="sectionA-2",
                        value=Decimal(4),
                    ),
                    "3": NodeSeed(
                        parent="sectionA-3",
                        value=Decimal(3),
                    ),
                }
            ),
            "sectionB": DefNodeSeed({"1": NodeSeed(parent="formA-1")}),
            "fieldB": DefNodeSeed(
                {"1": NodeSeed(parent="sectionB-1", value=Decimal(2))}
            ),
        }
    )

    return project_seed
