import pytest
from typing import List
from expert_dollup.app.dtos import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_should_be_able_to_scan_translations(
    ac, db_helper: DbFixtureHelper, mapper
):
    db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()
    project_definition = db.get_only_one(ProjectDefinition)

    translations = await AsyncCursor.all(
        ac,
        f"/api/translations/{project_definition.id}/en-US",
        unwrap_with=bind_page_dto(TranslationDto),
        after=make_sorter(lambda c: (c.name, c.id)),
    )

    expectd_en_translations = sorted(
        mapper.map_many(
            [
                translation
                for translation in db.all(Translation)
                if translation.locale == "en-US"
            ],
            TranslationDto,
        ),
        key=lambda c: (c.name, c.id),
    )

    assert len(translations) == len(expectd_en_translations)
    assert translations == expectd_en_translations
