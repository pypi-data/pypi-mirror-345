from typing import Optional, Tuple

from copit.models import FullAnalysis
from copit.models.location import Location
from copit.models.project import Project


def harmonize_ids(
    project: Project, location: Location, full_analysis: Optional[FullAnalysis] = None
) -> Tuple[Project, Location, Optional[FullAnalysis]]:
    project_id = project.project_id
    location_id = location.location_id
    location.project_id = project_id
    if full_analysis:
        full_analysis.analysis.project_id = project_id
        full_analysis.analysis.location_id = location_id
        full_analysis.cpt_data.project_id = project_id
        full_analysis.cpt_data.location_id = location_id
        full_analysis.cpt_data.analysis_id = full_analysis.analysis.id
        for lab_data in full_analysis.lab_data:
            lab_data.analysis_id = full_analysis.analysis.id
    return project, location, full_analysis
