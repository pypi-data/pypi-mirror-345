from enum import Enum

MIN_CPT_ALLOWED_STEP = 0.02


class AnalysisConfig(Enum):
    stratigraphy_plot_ncols = 5
    max_stratigraphy_layers = 6
    watch_parameters_precedence = 1


WATCHED = dict(precedence=AnalysisConfig.watch_parameters_precedence.value)
