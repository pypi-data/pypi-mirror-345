from dataclasses import dataclass, field

from ngi_calculations.cpt_correlations.definitions.geo import GEO


@dataclass(frozen=True)
class CptRawColumns:
    columns: dict = field(
        default_factory=lambda: {
            "A": "method_id",
            "B": GEO.depth.key,
            "C": GEO.qc.key,
            "D": GEO.fs.key,
            "E": GEO.u2.key,
            "F": GEO.temperature.key,
            "G": GEO.penetration_rate.key,
            "H": GEO.penetration_force.key,
            "I": GEO.tilt.key,
        }
    )


@dataclass(frozen=True)
class LabDataColumns:
    columns: dict = field(
        default_factory=lambda: {
            "A": GEO.depth.key,
            "B": GEO.wc.key,
            "C": GEO.WP.key,
            "D": GEO.LL.key,
            "E": GEO.Ip.key,
            "F": GEO.St.key,
            "G": GEO.uw.key,
            "H": GEO.u0.key,
        }
    )


@dataclass(frozen=True)
class CptProcessedColumns:
    columns: dict = field(
        default_factory=lambda: {
            **CptRawColumns().columns,
            "J": GEO.wc.key,
            "K": GEO.WP.key,
            "L": GEO.LL.key,
            "M": GEO.Ip.key,
            "N": GEO.St.key,
            "O": GEO.uw.key,
            "P": GEO.u0.key,
            "Q": GEO.cone_area_ratio.key,
            "R": GEO.sleeve_area_ratio.key,
            "S": GEO.sigVtTotal.key,
            "T": GEO.sigVtEff.key,
            "U": GEO.qt.key,
            "V": GEO.qn.key,
            "W": GEO.u_delta.key,
            "X": GEO.Fr.key,
            "Y": GEO.Qt.key,
            "Z": GEO.Bq.key,
            "AA": GEO.u_delta_norm.key,
            "AB": GEO.Ic.key,
            "AC": GEO.n.key,
            "AD": GEO.Qtn.key,
            "AE": GEO.Icn.key,
            "AF": GEO.Rf.key,
        }
    )
