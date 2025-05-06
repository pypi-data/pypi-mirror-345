from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class I18nVoc:
    eng: str
    nor: Optional[str] = None
    default_lang: str = "eng"

    @property
    def value(self) -> str:
        return self.__getattribute__(self.default_lang)

    def text(self, lang: Literal["eng", "nor"]) -> str:
        v = self.__getattribute__(lang)
        return v if v is not None else self.eng


@dataclass
class Vocabulary:
    lang: str = "eng"
    # spell-checker:disable
    easting_id: I18nVoc = field(default_factory=lambda: I18nVoc(eng="E", nor="Ø"))
    northing_id: I18nVoc = field(default_factory=lambda: I18nVoc(eng="N", nor="N"))
    elevation_id: I18nVoc = field(default_factory=lambda: I18nVoc(eng="Z", nor="Z"))
    client: I18nVoc = field(default_factory=lambda: I18nVoc(eng="client", nor="oppdragsgiver"))
    borehole: I18nVoc = field(default_factory=lambda: I18nVoc(eng="borehole", nor="borehull"))
    method: I18nVoc = field(default_factory=lambda: I18nVoc(eng="method", nor="metode"))
    date: I18nVoc = field(default_factory=lambda: I18nVoc(eng="date", nor="dato"))
    coordinates: I18nVoc = field(default_factory=lambda: I18nVoc(eng="coordinates", nor="koordinater"))
    coordinate_system: I18nVoc = field(default_factory=lambda: I18nVoc(eng="coordinate system", nor="koordinatsystem"))
    date_performed: I18nVoc = field(default_factory=lambda: I18nVoc(eng="date performed", nor="dato utført"))
    format: I18nVoc = field(default_factory=lambda: I18nVoc(eng="format", nor="format"))
    scale: I18nVoc = field(default_factory=lambda: I18nVoc(eng="scale", nor="målestokk"))
    revision: I18nVoc = field(default_factory=lambda: I18nVoc(eng="revision", nor="revisjon"))
    borehole_number: I18nVoc = field(default_factory=lambda: I18nVoc(eng="borehole num.", nor="sondenummer"))
    figure_number: I18nVoc = field(default_factory=lambda: I18nVoc(eng="figure num.", nor="figurnummer"))
    report_number: I18nVoc = field(default_factory=lambda: I18nVoc(eng="report num.", nor="rapportnummer"))
    application_class: I18nVoc = field(
        default_factory=lambda: I18nVoc(eng="application class", nor="anvendelsesklasse")
    )
    drawn_by: I18nVoc = field(default_factory=lambda: I18nVoc(eng="drawn by", nor="tegnet av"))
    controlled_by: I18nVoc = field(default_factory=lambda: I18nVoc(eng="controlled by", nor="Kontr. av:"))
    approved_by: I18nVoc = field(default_factory=lambda: I18nVoc(eng="approved by", nor="Godkjent av:"))
    # spell-checker:enable

    def __post_init__(self):
        for _, v in self.__dict__.items():
            if isinstance(v, I18nVoc):
                v.default_lang = self.lang

    def compound(self, words: list[str], lang: Optional[str] = None, sep: str = " ") -> str:
        lang_ = lang if lang else self.lang
        words_ = [self.__getattribute__(w).text(lang_) for w in words if hasattr(self, w)]
        if len(words_) > 0:
            return sep.join(words_)
        return "no word found"
