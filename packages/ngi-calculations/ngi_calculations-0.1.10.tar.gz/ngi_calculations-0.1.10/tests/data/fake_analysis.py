from typing import Optional

from faker import Faker
from copit.models import FullAnalysis
from copit.models.analysis import Analysis, AnalysisData, ExternalCptData, ExternalLabData


def fake_cpt_data():
    fake = Faker()
    cpt = ExternalCptData(
        project_id=fake.uuid4(),
        location_id=fake.uuid4(),
        analysis_id=fake.uuid4(),
        source=fake.pystr(),
        data=[],
    )
    return cpt


def fake_lab_data():
    fake = Faker()
    lab = ExternalLabData(
        id=fake.uuid4(),
        name=fake.name(),
        source=fake.uuid4(),
        analysis_id=fake.uuid4(),
        location_external_id=fake.uuid4(),
        project_external_id=fake.uuid4(),
        values=None,
        layers=None,
    )
    return lab


def fake_analysis():
    fake = Faker()
    analysis = Analysis(
        id=fake.uuid4(),
        name=fake.name(),
        project_id=fake.uuid4(),
        location_id=fake.uuid4(),
        data=AnalysisData(),
    )
    return analysis


# def harmonize_ids(full_analysis: FullAnalysis)->FullAnalysis:
#     project_id


# create a fake analysis using FullAnalysis in a function
def get_fake_full_analysis(lab_data_amount: Optional[int] = None) -> FullAnalysis:
    analysis = fake_analysis()
    cpt = fake_cpt_data()
    lab_data = [fake_lab_data() for _ in range(lab_data_amount)] if lab_data_amount else []
    # harmonize ids
    return FullAnalysis(analysis=analysis, cpt_data=cpt, lab_data=lab_data)
