import pytest
from typing import List
from expert_dollup.app.dtos import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_should_be_able_to_scan_translations(
    ac, expert_dollup_simple_project, mapper
):
    db = expert_dollup_simple_project
    assert len(db.project_definitions) == 1
    project_definition = db.project_definitions[0]

    translations = await AsyncCursor.all(
        ac,
        f"/api/translation/{project_definition.id}/en",
        after=normalize_request_results(TranslationDto, lambda c: (c["name"], c["id"])),
    )

    expectd_en_translations = normalize_dtos(
        mapper.map_many(
            [
                translation
                for translation in db.translations
                if translation.locale == "en"
            ],
            TranslationDto,
        ),
        lambda c: (c["name"], c["id"]),
    )

    assert len(translations) == len(expectd_en_translations)
    assert translations == expectd_en_translations