from dataclasses import dataclass

from ngi_calculations.cpt_correlations.models.geo import GeoParameter


@dataclass
class GeoParameters:
    easting = GeoParameter(
        key="easting", label="easting", unit="m", symbol="easting", value_range=(None, None), precision=0
    )

    northing = GeoParameter(
        key="northing", label="northing", unit="m", symbol="northing", value_range=(None, None), precision=0
    )

    latitude = GeoParameter(
        key="latitude", label="latitude", unit="deg", symbol="latitude", value_range=(-100, None), precision=0
    )

    longitude = GeoParameter(
        key="longitude", label="longitude", unit="deg", symbol="longitude", value_range=(-100, None), precision=0
    )

    point_y_wgs84_web = GeoParameter(
        key="point_y_wgs84_web",
        label="longitude",
        unit="deg",
        symbol="longitude",
        value_range=(None, None),
        precision=0,
    )

    point_x_wgs84_web = GeoParameter(
        key="point_x_wgs84_web", label="latitude", unit="deg", symbol="latitude", value_range=(None, None), precision=0
    )

    point_x_wgs84_pseudo = GeoParameter(
        key="point_x_wgs84_pseudo", label="easting", unit="m", symbol="easting", value_range=(None, None), precision=0
    )

    point_y_wgs84_pseudo = GeoParameter(
        key="point_y_wgs84_pseudo", label="northing", unit="m", symbol="northing", value_range=(None, None), precision=0
    )

    cone_area_ratio = GeoParameter(
        key="cone_area_ratio",
        label="cone_area_ratio",
        unit="-",
        symbol="cone_area_ratio",
        value_range=(None, None),
        precision=2,
        default_value=0.8,
    )

    sleeve_area_ratio = GeoParameter(
        key="sleeve_area_ratio",
        label="sleeve_area_ratio",
        unit="-",
        symbol="sleeve_area_ratio",
        value_range=(None, None),
        precision=2,
        default_value=1.0,
    )

    depth = GeoParameter(
        key="depth", label="depth", unit="m", symbol="depth", value_range=(0, None), precision=2, percentile_precision=0
    )

    to = GeoParameter(key="to", label="to", unit="m", symbol="to", value_range=(0, None), precision=2)

    depth_raw = GeoParameter(key="depth_raw", label="raw depth", unit="m", symbol="depth", precision=2)
    depth_from = GeoParameter(key="from", label="From", unit="m", precision=2, tabulator_editor="")
    depth_to = GeoParameter(key="to", label="To", unit="m", precision=2)
    depth_tilt = GeoParameter(key="depth_tilt", label="tilt depth", unit="m", symbol="depth", precision=2)

    soil_type = GeoParameter(
        key="soil_type",
        label="Soil type",
        unit="-",
        tabulator_type="text",
        tabulator_editor="list",
        tabulator_editor_params={"values": ["skip", "clay", "sand"]},
    )

    u0 = GeoParameter(
        key="u0",
        label="pore pressure",
        unit="kPa",
        symbol="u0",
        value_range=(0, 1000),
        precision=1,
        axis_scaling_base=False,
    )

    tilt = GeoParameter(key="tilt", label="tilt", unit="deg", symbol="tilt", value_range=(0, 10), precision=0)

    penetration_rate = GeoParameter(
        key="penetration_rate",
        label="penetration rate",
        unit="mm/s",
        symbol="penetration rate",
        value_range=(None, None),
        precision=0,
    )

    penetration_force = GeoParameter(
        key="penetration_force",
        label="penetration force",
        unit="kN",
        symbol="penetration force",
        value_range=(None, None),
        precision=0,
    )

    temperature = GeoParameter(
        key="temperature",
        label="temperature",
        unit="deg",
        # unit="degree Celsius",
        symbol="temperature",
        value_range=(0, 20),
        precision=0,
    )

    uw = GeoParameter(
        key="uw",
        label="unit weight",
        unit="kN/m3",
        symbol="UW",
        value_range=(16, 22),
        precision=2,
        axis_scaling_base=False,
    )

    wc = GeoParameter(key="wc", label="water content", unit="%", symbol="WC", value_range=(10, 60), precision=1)

    LL = GeoParameter(key="LL", label="liquid limit", unit="%", symbol="WL")

    WP = GeoParameter(key="WP", label="plastic limit", unit="%", symbol="WP")

    Ip = GeoParameter(
        key="Ip",
        label="plasticity index",
        unit="-",
        symbol="Ip",
        value_range=(0, 30),
        precision=1,
        axis_scaling_base=1,
    )

    OCR = GeoParameter(
        key="OCR",
        label="over-consolidation ratio",
        unit="-",
        symbol="OCR",
        value_range=(0, 20),
        precision=2,
        percentile_precision=0,
    )

    Vs = GeoParameter(
        key="Vs",
        label="Shear wave velocity",
        unit="m/s",
        symbol="Vs",
        default_value=200,
        value_range=(0, 600),
        precision=0,
    )

    Su = GeoParameter(
        key="Su",
        label="undrained shear strength",
        unit="kPa",
        symbol="Cu",
        default_value=10,
        value_range=(0, 150),
        precision=1,
    )

    Su_Fc = GeoParameter(key="Su_Fc", label="Su from Fallcone", unit="kPa", symbol="Cu, Fc")

    Su_rem = GeoParameter(key="Su_rem", label="Su remolded", unit="kPa", symbol="Cu - rem")

    Su_Fc_rem = GeoParameter(key="Su_Fc_rem", label="Su remolded from Fallcone", unit="kPa", symbol="Cu, Fc - rem")
    Su_UCS_rem = GeoParameter(key="Su_UCS_rem", label="Su remolded from UCS", unit="kPa", symbol="Cu, UCS - rem")

    Su_UU = GeoParameter(key="Su_UU", label="Su from UU", unit="kPa", symbol="Cu, UU")

    Su_UC = GeoParameter(key="Su_UC", label="Su from UC", unit="kPa", symbol="Cu, UC")

    Su_UCS = GeoParameter(key="Su_UCS", label="Su from UCS", unit="kPa", symbol="Cu, UCS")

    Su_CAUc = GeoParameter(key="Su_CAUc", label="Su from CAUc", unit="kPa", symbol="Cu, CAUc")

    St = GeoParameter(
        key="St",
        label="sensitivity",
        unit="-",
        symbol="St",
        value_range=(0, 30),
        precision=1,
        axis_scaling_base=1,
    )

    St_Fc = GeoParameter(key="St_Fc", label="sensitivity from Fallcone", unit="-", symbol="St, Fc")

    St_UU = GeoParameter(key="St_UU", label="sensitivity from UU", unit="-", symbol="St, UU")

    St_UCS = GeoParameter(key="St_UCS", label="sensitivity from UCS", unit="-", symbol="St, UCS")

    axialStrainFailure_UCS = GeoParameter(
        key="AxialStrainFailure_UCS", label="AxialStrainFailure from UCS", unit="%", symbol="AxialStrainFailure, UCS"
    )

    qc = GeoParameter(
        key="qc",
        label="cone resistance",
        legend_="measured",
        # legend_="measured cone tip resistance",
        legend_group="cone tip resistance",
        unit="MPa",
        symbol="qc",
        value_range=(0, None),
        precision=1,
    )

    qn = GeoParameter(
        key="qn",
        label="normalized cone resistance",
        unit="MPa",
        symbol="qn",
        equation=r"$q_{net} = 1000 * q_{t} - \sigma_v^{total}$",
        value_range=(0, None),
    )

    fs = GeoParameter(
        key="fs",
        label="sleeve friction",
        unit="kPa",
        symbol="fs",
        value_range=(0, None),
        precision=0,
    )

    u2 = GeoParameter(
        key="u2",
        label="pore pressure",
        unit="kPa",
        symbol="u2",
        value_range=(0, None),
        precision=0,
    )

    u2_raw = GeoParameter(key="u2_raw", label="raw pore pressure", unit="kPa", symbol="u2_raw")

    u_delta = GeoParameter(key="u_delta", label="differential pressure", unit="kPa", symbol="u_delta")

    u_delta_norm = GeoParameter(
        key="u_delta_norm", label="differential pressure normalized", unit="-", symbol="u_delta_norm"
    )

    sigV = GeoParameter(key="sigV", label="vertical stress", unit="kPa", symbol="sig_v", value_range=(0, None))

    DR = GeoParameter(key="DR", label="relative density", unit="%", symbol="DR", value_range=(0, 100), precision=0)

    modulus = GeoParameter(key="M0", label="Modulus", unit="MPa", symbol="M0", value_range=(0, 50))

    M0 = GeoParameter(
        key="M0",
        label="Modulus",
        unit="MPa",
        symbol="M0",
        value_range=(0, 50),
        precision=0,
    )

    phiEff = GeoParameter(
        key="phiEff", label="effective friction angle", unit="deg", symbol="φ'", value_range=(0, 60), precision=1
    )

    p_cons = GeoParameter(
        key="p_cons", label="pre-consolidation pressure", unit="kPa", symbol="pc'", value_range=(0, 500), precision=0
    )

    OCR_Profile_BE = GeoParameter(key="OCR_Profile_BE", label="OCR", unit="-", symbol="OCR_Profile_BE")

    OCR_Bq = GeoParameter(key="OCR_Bq", label="OCR from Bq", unit="-", symbol="OCR_Bq")

    OCR_Qt = GeoParameter(key="OCR_Qt", label="OCR from Qt", unit="-", symbol="OCR_Qt")

    OCR_SHANSEP = GeoParameter(key="OCR_SHANSEP", label="OCR from Elevation", unit="-", symbol="OCR_SHANSEP")

    OCR_Pressure = GeoParameter(key="OCR_Pressure", label="OCR from Pressure", unit="-", symbol="OCR_Pressure")

    Nkt_Karlsrud = GeoParameter(key="Nkt_Karlsrud", label="Nkt", unit="-", symbol="Nkt_Karlsrud")

    Su_Nkt_Karlsrud = GeoParameter(key="Su_Nkt_Karlsrud", label="Su_Nkt_Karlsrud", unit="KPa", symbol="Cu_Nkt_Karlsrud")

    Ndu_Karlsrud = GeoParameter(key="Ndu_Karlsrud", label="Ndu_Karlsrud", unit="-", symbol="Ndu_Karlsrud")

    Su_Ndu_Karlsrud = GeoParameter(key="Su_Ndu_Karlsrud", label="Su_Ndu_Karlsrud", unit="KPa", symbol="Cu_Ndu_Karlsrud")

    Su_NC_Karlsrud = GeoParameter(key="Su_NC_Karlsrud", label="Su_NC_Karlsrud", unit="KPa", symbol="Cu_NC_Karlsrud")

    Su_SHANSEP = GeoParameter(key="Su_SHANSEP", label="Su_SHANSEP", unit="KPa", symbol="Cu_SHANSEP")

    sigVtTotal = GeoParameter(
        key="sigVtTotal",
        label="Total vertical stress",
        unit="kPa",
        symbol="sig_v tot",
        equation="""prev.sigVtTotal + 0.5 * (x.uw + prev.uw) * (x.depth - prev.depth)""",
        legend_="σ v,total",
        value_range=(0, None),
    )

    sigVtEff = GeoParameter(
        key="sigVtEff",
        label="Effective vertical stress",
        unit="kPa",
        symbol="sig_v eff",
        equation=r"$\sigma_v^{eff} = \max( \sigma_v^{total} - u_0 ; 0 )$",
        value_range=(0, None),
        legend_="σ v,eff",
    )
    stress = GeoParameter(
        key="stress",
        label="Vertical stress / in-situ pressure",
        unit="kPa",
        symbol="stress",
        # equation="$\sigma_v^{eff} = \max( \sigma_v^{total} - u_0 ; 0 )$",
        # value_range=(0, None),
        # legend_="σ v,eff",
    )

    elevation = GeoParameter(key="elevation", label="Elevation", unit="m", symbol="Elevation")

    qt = GeoParameter(
        key="qt",
        label="total cone resistance",
        axis_title="Cone resistance",
        legend_="corrected",
        # legend_="corrected cone tip resistance",
        legend_group="cone tip resistance",
        unit="MPa",
        symbol="qt",
        equation="$qt = 1000 * qc + u_2 * (1 - \alpha) * k$",
        value_range=(0, None),
    )

    Qt = GeoParameter(
        key="Qt",
        label="normalized cone resistance",
        unit="-",
        symbol="Qt",
        equation=r"$Qt = ( 1000 * qt - \sigma_v^{total} ) / \sigma_v^{eff}$",
        value_range=(0, None),
    )

    Bq = GeoParameter(
        key="Bq",
        label="pore pressure factor",
        # label="normalized pressure",
        unit="-",
        symbol="Bq",
        equation=r"$Bq = ( u_2 - u_0 ) / ( 1000 * qt - \sigma_v^{total} )$",
        value_range=(0, None),
    )

    Rf = GeoParameter(
        key="Rf",
        label="friction ratio",
        unit="%",
        symbol="Rf",
        equation="$Rf = 100 * fs / ( 1000 * qc )$",
        value_range=(0, None),
    )

    Fr = GeoParameter(
        key="Fr",
        label="normalized friction ratio",
        unit="%",
        symbol="Fr",
        equation=r"$Fr = fs / ( 1000 * qt - \sigma_v^{total} ) * 100\%$",
        value_range=(0, None),
    )

    Ic = GeoParameter(
        key="Ic",
        label="soil behavior index",
        unit="-",
        symbol="Ic",
        equation=r"$Ic = \sqrt{( 3.47 - \log Qt)^2 + (\log Fr + 1.22)^2 }$",
    )

    n = GeoParameter(
        key="n",
        label="exponent for normalized soil behavior index",
        unit="-",
        symbol="n",
        equation=r"$n = \min \left( 0.381 * Ic + 0.05 * (\sigma_v^{eff} / p_{Atm}) - 0.15 ), 1.0\right)$",
    )

    Qtn = GeoParameter(
        key="Qtn",
        label="normalized cone resistance by n exponent",
        unit="-",
        symbol="Qtn",
        equation=r"$Qtn = Qt * \left( \frac{p_{Atm}}{\sigma_v^{eff}}\right)^{n - 1}$",
    )

    Icn = GeoParameter(
        key="Icn",
        label="normalized soil behavior index",
        axis_title="SBT",
        unit="-",
        symbol="Icn",
        equation=r"$Icn =  \sqrt{\left( 3.47 - \\frac{\log Qtn}{\log 10} \\right)^2 + \left(\\frac{\log Fr}{\log 10} + 1.22 \\right)^2 }$",
        legend_="Icn (Robertson, 2009)",
        value_range=(0, 4.5),
    )

    color = GeoParameter(key="color", label="color", unit="-", symbol="color")
    desc_main = GeoParameter(key="desc_main", label="Main desc", unit="-", symbol="desc_main")
    desc_secondary = GeoParameter(key="desc_secondary", label="Secondary desc", unit="-", symbol="desc_secondary")
    desc_tertiary = GeoParameter(key="desc_tertiary", label="Tertiary desc", unit="-", symbol="desc_tertiary")


GEO = GeoParameters()
