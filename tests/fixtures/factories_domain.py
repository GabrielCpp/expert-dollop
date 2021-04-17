import factory
from uuid import uuid4, UUID
from datetime import datetime, timezone
from expert_dollup.core.domains import *


class ProjectDefinitionNodeFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNode

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"node{n}")
    is_collection = False
    instanciate_by_default = True
    order_index = factory.Sequence(lambda n: n)
    config = NodeConfig()
    default_value = None
    path = []
    creation_date_utc = factory.Sequence(lambda n: datetime.now(timezone.utc))
