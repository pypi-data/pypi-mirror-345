from enum import Enum
from typing import Literal


class ImpressoNamedEntityRecognitionEntityType(str, Enum):
    COMP_DEMONYM = "comp.demonym"
    COMP_FUNCTION = "comp.function"
    COMP_NAME = "comp.name"
    COMP_QUALIFIER = "comp.qualifier"
    COMP_TITLE = "comp.title"
    LOC = "loc"
    LOC_ADD_ELEC = "loc.add.elec"
    LOC_ADD_PHYS = "loc.add.phys"
    LOC_ADM_NAT = "loc.adm.nat"
    LOC_ADM_REG = "loc.adm.reg"
    LOC_ADM_SUP = "loc.adm.sup"
    LOC_ADM_TOWN = "loc.adm.town"
    LOC_FAC = "loc.fac"
    LOC_ORO = "loc.oro"
    LOC_PHYS_ASTRO = "loc.phys.astro"
    LOC_PHYS_GEO = "loc.phys.geo"
    LOC_PHYS_HYDRO = "loc.phys.hydro"
    LOC_UNK = "loc.unk"
    ORG = "org"
    ORG_ADM = "org.adm"
    ORG_ENT = "org.ent"
    ORG_ENT_PRESSAGENCY = "org.ent.pressagency"
    ORG_ENT_PRESSAGENCY_AFP = "org.ent.pressagency.AFP"
    ORG_ENT_PRESSAGENCY_AG = "org.ent.pressagency.ag"
    ORG_ENT_PRESSAGENCY_ANSA = "org.ent.pressagency.ANSA"
    ORG_ENT_PRESSAGENCY_AP = "org.ent.pressagency.AP"
    ORG_ENT_PRESSAGENCY_APA = "org.ent.pressagency.APA"
    ORG_ENT_PRESSAGENCY_ATS_SDA = "org.ent.pressagency.ATS-SDA"
    ORG_ENT_PRESSAGENCY_BELGA = "org.ent.pressagency.Belga"
    ORG_ENT_PRESSAGENCY_CTK = "org.ent.pressagency.CTK"
    ORG_ENT_PRESSAGENCY_DDP_DAPD = "org.ent.pressagency.DDP-DAPD"
    ORG_ENT_PRESSAGENCY_DNB = "org.ent.pressagency.DNB"
    ORG_ENT_PRESSAGENCY_DOMEI = "org.ent.pressagency.Domei"
    ORG_ENT_PRESSAGENCY_DPA = "org.ent.pressagency.DPA"
    ORG_ENT_PRESSAGENCY_EUROPAPRESS = "org.ent.pressagency.Europapress"
    ORG_ENT_PRESSAGENCY_EXTEL = "org.ent.pressagency.Extel"
    ORG_ENT_PRESSAGENCY_HAVAS = "org.ent.pressagency.Havas"
    ORG_ENT_PRESSAGENCY_KIPA = "org.ent.pressagency.Kipa"
    ORG_ENT_PRESSAGENCY_REUTERS = "org.ent.pressagency.Reuters"
    ORG_ENT_PRESSAGENCY_SPK_SMP = "org.ent.pressagency.SPK-SMP"
    ORG_ENT_PRESSAGENCY_STEFANI = "org.ent.pressagency.Stefani"
    ORG_ENT_PRESSAGENCY_TASS = "org.ent.pressagency.TASS"
    ORG_ENT_PRESSAGENCY_UNK = "org.ent.pressagency.unk"
    ORG_ENT_PRESSAGENCY_UP_UPI = "org.ent.pressagency.UP-UPI"
    ORG_ENT_PRESSAGENCY_WOLFF = "org.ent.pressagency.Wolff"
    ORG_ENT_PRESSAGENCY_XINHUA = "org.ent.pressagency.Xinhua"
    PERS = "pers"
    PERS_COLL = "pers.coll"
    PERS_IND = "pers.ind"
    PERS_IND_ARTICLEAUTHOR = "pers.ind.articleauthor"
    PROD = "prod"
    PROD_DOCTR = "prod.doctr"
    PROD_MEDIA = "prod.media"
    TIME = "time"
    TIME_DATE_ABS = "time.date.abs"
    TIME_HOUR_ABS = "time.hour.abs"
    UNK = "unk"

    def __str__(self) -> str:
        return str(self.value)


ImpressoNamedEntityRecognitionEntityTypeLiteral = Literal[
    "comp.demonym",
    "comp.function",
    "comp.name",
    "comp.qualifier",
    "comp.title",
    "loc",
    "loc.add.elec",
    "loc.add.phys",
    "loc.adm.nat",
    "loc.adm.reg",
    "loc.adm.sup",
    "loc.adm.town",
    "loc.fac",
    "loc.oro",
    "loc.phys.astro",
    "loc.phys.geo",
    "loc.phys.hydro",
    "loc.unk",
    "org",
    "org.adm",
    "org.ent",
    "org.ent.pressagency",
    "org.ent.pressagency.AFP",
    "org.ent.pressagency.ag",
    "org.ent.pressagency.ANSA",
    "org.ent.pressagency.AP",
    "org.ent.pressagency.APA",
    "org.ent.pressagency.ATS-SDA",
    "org.ent.pressagency.Belga",
    "org.ent.pressagency.CTK",
    "org.ent.pressagency.DDP-DAPD",
    "org.ent.pressagency.DNB",
    "org.ent.pressagency.Domei",
    "org.ent.pressagency.DPA",
    "org.ent.pressagency.Europapress",
    "org.ent.pressagency.Extel",
    "org.ent.pressagency.Havas",
    "org.ent.pressagency.Kipa",
    "org.ent.pressagency.Reuters",
    "org.ent.pressagency.SPK-SMP",
    "org.ent.pressagency.Stefani",
    "org.ent.pressagency.TASS",
    "org.ent.pressagency.unk",
    "org.ent.pressagency.UP-UPI",
    "org.ent.pressagency.Wolff",
    "org.ent.pressagency.Xinhua",
    "pers",
    "pers.coll",
    "pers.ind",
    "pers.ind.articleauthor",
    "prod",
    "prod.doctr",
    "prod.media",
    "time",
    "time.date.abs",
    "time.hour.abs",
    "unk",
]
