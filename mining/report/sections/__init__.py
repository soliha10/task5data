from .cover import cover_page
from .episodes import episode_sections
from .methodology import methodology_section
from .mines import mine_sections
from .overview import overview_section
from .summary import executive_summary, flag_counts_section, statistics_section

SECTION_BUILDERS = (
    cover_page,
    executive_summary,
    statistics_section,
    flag_counts_section,
    overview_section,
    mine_sections,
    episode_sections,
    methodology_section,
)
__all__ = ["SECTION_BUILDERS"]
