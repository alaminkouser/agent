from agent_skills import SkillsManager, SkillContext, SkillSearchResult, Skill
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / ".." / ".DATA/skills"

SKILLS_MANAGER = SkillsManager(SKILLS_DIR)


class skills:
    def skills_discover() -> list[Skill]:
        """
        Discover all skills.
        """
        return SKILLS_MANAGER.discover()

    def skills_create(
        name: str, description: str, content: str, tags: list[str]
    ) -> Skill:
        """
        Create a new skill. If you need to remember or told to do something in a very specific way, create a skill.
        To create a skill, you need to provide the following information:
        - name: The name of the skill. This is usually a kebab-case string.
        - description: The description of the skill. This is a short summary of what the skill does.
        - content: The content of the skill. This should contain the actual instructions for the skill. And use markdown format.
        - tags: The tags of the skill. This is a list of tags that describe the skill. Use kebab-case for tags.

        Before creating a skill, search with all possible queries to avoid duplicates.

        To search for a skill, use skills_search tool.
        """
        return SKILLS_MANAGER.create(
            name=name,
            description=description,
            content=content,
            tags=tags,
            context=SkillContext.FORK,
        )

    def skills_read(name: str) -> Optional[Skill]:
        """
        Read a skill. If you want to do a thing in a very specific way, read a skill first.
        - name: The name of the skill. This is a kebab-case string.
        """
        return SKILLS_MANAGER.get(name)

    def skills_search(query: str) -> SkillSearchResult:
        """
        Search for skills that match the query.
        - query: The query to search for.

        It is suggest to use one or two words for the query.
        """
        return SKILLS_MANAGER.search(query, limit=100)
