import os
from typing import Annotated, Literal

from pydantic import Field

from bayesline.api._src.registry import Settings, SettingsMenu, SettingsTypeMetaData


class PortfolioUploadSettings(Settings):
    """
    Specifies options for a portfolio upload, such as the parser etc.
    """

    parser: str = Field(description=("The parser to use."))
    portfolio_ids: list[str] = Field(
        description=("The available portfolio IDs that are contained in this upload.")
    )


class PortfolioUploadSettingsMenu(
    SettingsMenu[PortfolioUploadSettings], frozen=True, extra="forbid"
):

    parsers: list[str] = Field(
        description=(
            "The list of available parsers that can be used "
            "to parse the portfolio files."
        )
    )

    def describe(self, settings: PortfolioUploadSettings | None = None) -> str:
        if settings is None:
            return f"Parsers: [{', '.join(self.parsers)}]"
        else:
            all_ids = settings.portfolio_ids
            return (
                f"Parser: {settings.parser}{os.linesep}"
                f"Available Portfolios: {', '.join(all_ids)}"
            )

    def validate_settings(self, settings: PortfolioUploadSettings) -> None:
        if settings.parser not in self.parsers:
            raise ValueError(
                f"Invalid parser: {settings.parser}. "
                f"Available parsers are: {', '.join(self.parsers)}"
            )


class PortfolioOrganizerSettings(Settings):
    """
    Specifies which portfolios to enable (from different sources).

    Different sources (e.g. uploaded portfolios) can provide the same portfolio
    identifiers. These settings allow to specify which portfolios to enable from
    which sources.
    """

    enabled_portfolios: Annotated[
        dict[str, str],
        Field(
            description=(
                "The enabled portfolios from different sources. "
                "The key is the portfolio ID, and the value is the source "
                "(name of the underlying portfolio service)."
            ),
        ),
        SettingsTypeMetaData[dict[str, str]](
            references=PortfolioUploadSettings,
            extractor=lambda v: list(set(v.values())),
        ),
    ]


class PortfolioOrganizerSettingsMenu(
    SettingsMenu[PortfolioOrganizerSettings], frozen=True, extra="forbid"
):

    sources: dict[str, list[str]] = Field(
        description=(
            "Mapping of sources to the available portfolio IDs for that source."
        )
    )

    def describe(self, settings: PortfolioOrganizerSettings | None = None) -> str:
        if settings is None:
            return f"Sources: {self.sources}"
        else:
            enabled_portfolios = settings.enabled_portfolios
            return f"Enabled Portfolios: {enabled_portfolios}"

    def validate_settings(self, settings: PortfolioOrganizerSettings) -> None:
        messages = []
        for portfolio_id, source in settings.enabled_portfolios.items():
            if source not in self.sources:
                messages.append(
                    f"Invalid source: {source}. "
                    f"Available sources: {', '.join(self.sources.keys())}. "
                )
            elif portfolio_id not in self.sources[source]:
                messages.append(
                    f"Invalid portfolio ID: {portfolio_id} for source {source}. "
                )
        if messages:
            raise ValueError("".join(messages))


class PortfolioSettings(Settings):
    """
    Specifies different options of obtaining portfolios.
    """

    portfolio_schema: Annotated[
        str | int | PortfolioOrganizerSettings,
        Field(
            description=(
                "The portfolio organizer settings to use as an underlying schema of "
                "portfolios. The 'Default' schema is used by default."
            ),
        ),
        SettingsTypeMetaData[str | int | PortfolioOrganizerSettings](
            references=PortfolioOrganizerSettings
        ),
    ]
    ffill: Literal["no-ffill", "ffill-with-drift"] = "no-ffill"
    unpack: Literal["no-unpack", "unpack"] = "no-unpack"


class PortfolioSettingsMenu(
    SettingsMenu[PortfolioSettings], frozen=True, extra="forbid"
):
    """
    Specifies the set of available options that
    can be used to create portfolio settings.
    """

    schemas: list[str] = Field(
        description=(
            "The available schemas (i.e. names from the portfolio organizer)."
        ),
        default_factory=list,
    )

    def describe(self, settings: PortfolioSettings | None = None) -> str:
        if settings is None:
            return (
                f"Schemas: {', '.join(self.schemas)}\n"
                "Forward Fill Options: 'no-ffill', 'ffill-with-drift'\n"
                "Unpack Options: 'no-unpack', 'unpack"
            )
        else:
            return f"Forward Fill: {settings.ffill}\nUnpack: {settings.unpack}"

    def validate_settings(self, settings: PortfolioSettings) -> None:
        s = settings.portfolio_schema
        if isinstance(s, str) and s not in self.schemas:
            raise ValueError(
                f"Invalid schema: {settings.portfolio_schema}. "
                f"Available schemas are: {', '.join(self.schemas)}"
            )
