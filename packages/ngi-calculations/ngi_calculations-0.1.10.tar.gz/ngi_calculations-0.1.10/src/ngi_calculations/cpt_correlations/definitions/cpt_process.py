from copit.base.base_enum import BaseParameter, BaseParameters


class CptProcessParameters(BaseParameters):

    sigVtTotal = BaseParameter(
        label="Total vertical stress",
        unit="kPa",
        symbol="sig_v tot",
        equation="""prev.sigVtTotal + 0.5 * (x.uw + prev.uw) * (x.depth - prev.depth)""",
    )

    sigVtEff = BaseParameter(
        label="Effective vertical stress",
        unit="kPa",
        symbol="sig_v eff",
        equation="""
            $$
            \sigma_v^{eff} = \max( \sigma_v^{total} - u_0 ; 0 )
            $$
        """,
    )

    elevation = BaseParameter(label="Elevation", unit="m", symbol="Elevation")
    qt = BaseParameter(label="total cone resistance", unit="MPa", symbol="qt")
    Qt = BaseParameter(
        label="normalized cone resistance",
        unit="-",
        symbol="Qt",
        equation="""
            x => (1000 * x.qt - x.sigVtTotal) / x.sigVtEff)
        """,
    )
    Bq = BaseParameter(
        label="normalized pressure",
        unit="-",
        symbol="Bq",
        equation="""
            x =>  (x.u2 - x.porePressure) / (1000 * x.qt - x.sigVtTotal)
        """,
    )
    Rf = (
        BaseParameter(
            label="friction ratio",
            unit="%",
            symbol="Rf",
            equation="""
            compose(onlyFinite, x =>  100 * x.fs / (1000  * x.qc),)
        """,
        ),
    )
    Fr = BaseParameter(
        label="normalized friction ratio",
        unit="%",
        symbol="Fr",
        equation="""
            compose(onlyFinite, multiply(100), x =>  x.fs / (1000 * x.qt - x.sigVtTotal))
        """,
    )
    Ic = BaseParameter(
        label="soil behavior index",
        unit="-",
        symbol="Ic",
        equation="""
            Math.sqrt((3.47 - Math.log(x.Qt)) ** 2.0 + (Math.log(x.Fr) + 1.22) ** 2.0)
        """,
    )
    n = BaseParameter(
        label="exponent for normalized soil behavior index",
        unit="-",
        symbol="n",
        equation="""
            Math.min(0.381 * Ic + 0.05 * (x.sigVtEff / pAtm) - 0.15, 1.0)
        """,
    )
    Qtn = BaseParameter(
        label="normalized cone resistance by n exponent",
        unit="-",
        symbol="Qtn",
        equation="""
             x.Qt * (pAtm / x.sigVtEff) ** (n - 1)
        """,
    )
    Icn = BaseParameter(
        label="normalized soil behavior index",
        unit="-",
        symbol="Icn",
        equation="""
                const a = 3.47 - Math.log(Qtn) / Math.log(10)
                const b = Math.log(x.Fr) / Math.log(10) + 1.22
                const result = Math.sqrt(a * a + b * b)
                return onlyFinite(result)
        """,
    )
