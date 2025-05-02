"""Species"""

from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from aind_data_schema_models.registries import Registry


class StrainModel(BaseModel):
    """Base model for a strain"""

    model_config = ConfigDict(frozen=True)
    name: str
    species: str
    registry: Registry.ONE_OF
    registry_identifier: str


class _C57Bl_6J(StrainModel):
    """Model C57BL/6J"""

    name: Literal["C57BL/6J"] = "C57BL/6J"
    species: Literal["Mus musculus"] = "Mus musculus"
    registry: Registry.ONE_OF = Registry.MGI
    registry_identifier: Literal["MGI:3028467"] = "MGI:3028467"


class _Balb_C(StrainModel):
    """Model BALB/c"""

    name: Literal["BALB/c"] = "BALB/c"
    species: Literal["Mus musculus"] = "Mus musculus"
    registry: Registry.ONE_OF = Registry.MGI
    registry_identifier: Literal["MGI:2159737"] = "MGI:2159737"


class Strain:
    """Strain"""

    C57BL_6J = _C57Bl_6J()

    BALB_C = _Balb_C()

    ALL = tuple(StrainModel.__subclasses__())

    ONE_OF = Annotated[Union[tuple(StrainModel.__subclasses__())], Field(discriminator="name")]


class SpeciesModel(BaseModel):
    """Base model for species"""

    model_config = ConfigDict(frozen=True)
    name: str
    registry: Registry.ONE_OF
    registry_identifier: str


class _Callithrix_Jacchus(SpeciesModel):
    """Model Callithrix jacchus"""

    name: Literal["Callithrix jacchus"] = "Callithrix jacchus"
    registry: Registry.ONE_OF = Registry.NCBI
    registry_identifier: Literal["NCBI:txid9483"] = "NCBI:txid9483"


class _Homo_Sapiens(SpeciesModel):
    """Model Homo sapiens"""

    name: Literal["Homo sapiens"] = "Homo sapiens"
    registry: Registry.ONE_OF = Registry.NCBI
    registry_identifier: Literal["NCBI:txid9606"] = "NCBI:txid9606"


class _Macaca_Mulatta(SpeciesModel):
    """Model Macaca mulatta"""

    name: Literal["Macaca mulatta"] = "Macaca mulatta"
    registry: Registry.ONE_OF = Registry.NCBI
    registry_identifier: Literal["NCBI:txid9544"] = "NCBI:txid9544"


class _Mus_Musculus(SpeciesModel):
    """Model Mus musculus"""

    name: Literal["Mus musculus"] = "Mus musculus"
    registry: Registry.ONE_OF = Registry.NCBI
    registry_identifier: Literal["NCBI:txid10090"] = "NCBI:txid10090"


class _Rattus_Norvegicus(SpeciesModel):
    """Model Rattus norvegicus"""

    name: Literal["Rattus norvegicus"] = "Rattus norvegicus"
    registry: Registry.ONE_OF = Registry.NCBI
    registry_identifier: Literal["NCBI:txid10116"] = "NCBI:txid10116"


class Species:
    """Species"""

    CALLITHRIX_JACCHUS = _Callithrix_Jacchus()
    HOMO_SAPIENS = _Homo_Sapiens()
    MACACA_MULATTA = _Macaca_Mulatta()
    MUS_MUSCULUS = _Mus_Musculus()
    RATTUS_NORVEGICUS = _Rattus_Norvegicus()

    ALL = tuple(SpeciesModel.__subclasses__())

    ONE_OF = Annotated[Union[tuple(SpeciesModel.__subclasses__())], Field(discriminator="name")]
