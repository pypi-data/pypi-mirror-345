import datetime as dt
import io
from typing import Any, Literal

import polars as pl
from bayesline.api import AsyncSettingsRegistry, RawSettings, SettingsRegistry
from bayesline.api.equity import (
    AsyncPortfolioApi,
    AsyncPortfolioLoaderApi,
    AsyncPortfolioParserApi,
    AsyncPortfolioUploadApi,
    AsyncPortfolioUploadLoaderApi,
    PortfolioApi,
    PortfolioLoaderApi,
    PortfolioOrganizerSettings,
    PortfolioOrganizerSettingsMenu,
    PortfolioParserApi,
    PortfolioParserResult,
    PortfolioSettings,
    PortfolioSettingsMenu,
    PortfolioUploadApi,
    PortfolioUploadError,
    PortfolioUploadLoaderApi,
    PortfolioUploadSettings,
    PortfolioUploadSettingsMenu,
)
from bayesline.api.types import DateLike, IdType, to_date

from bayesline.apiclient._src.client import ApiClient, AsyncApiClient
from bayesline.apiclient._src.settings import (
    AsyncHttpSettingsRegistryClient,
    HttpSettingsRegistryClient,
)


class AsyncPortfolioClientImpl(AsyncPortfolioApi):

    def __init__(self, client: AsyncApiClient, settings: PortfolioSettings):
        self._client = client
        self._settings = settings

    @property
    def name(self) -> str:
        return (
            self._client.sync()
            .post("name", body={"settings": self._settings.model_dump()})
            .json()
        )

    async def get_id_types(self) -> dict[str, list[IdType]]:
        return (
            await self._client.post(
                "id-types", body={"settings": self._settings.model_dump()}
            )
        ).json()

    async def get_coverage(
        self,
        names: str | list[str] | None = None,
        *,
        by: Literal["date", "asset"] = "date",
        metric: Literal["count", "holding"] = "count",
        stats: list[str] | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {"by": str(by), "metric": str(metric)}
        if stats is not None:
            params["stats"] = stats
        response = await self._client.post(
            "coverage",
            params=params,
            body={"names": names, "settings": self._settings.model_dump()},
        )
        if response.status_code == 404:
            raise KeyError(response.json()["detail"])
        elif response.status_code == 400:
            raise ValueError(response.json()["detail"])
        return pl.read_parquet(io.BytesIO(response.content))

    async def get_portfolio_names(self) -> list[str]:
        response = await self._client.post(
            "names", body={"settings": self._settings.model_dump()}
        )
        return response.json()

    async def get_portfolio_groups(self) -> dict[str, list[str]]:
        response = await self._client.post(
            "groups", body={"settings": self._settings.model_dump()}
        )
        return response.json()

    async def get_dates(
        self, names: list[str] | str | None = None, *, collapse: bool = False
    ) -> dict[str, list[dt.date]]:
        response = await self._client.post(
            "dates",
            params={"collapse": collapse},
            body={"names": names, "settings": self._settings.model_dump()},
        )
        response_data = response.json()
        if response.status_code == 404:
            raise KeyError(response_data["detail"])
        elif response.status_code == 400:
            raise ValueError(response_data["detail"])
        return {p: [to_date(d) for d in response_data[p]] for p in response_data.keys()}

    async def get_portfolio(
        self,
        names: list[str] | str,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        response = await self._client.post(
            "data",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "id_type": id_type,
            },
            body={"names": names, "settings": self._settings.model_dump()},
        )
        if response.status_code == 404:
            raise KeyError(response.json()["detail"])
        elif response.status_code == 400:
            raise ValueError(response.json()["detail"])
        return pl.read_parquet(io.BytesIO(response.content))


class PortfolioClientImpl(PortfolioApi):

    def __init__(self, client: ApiClient, settings: PortfolioSettings):
        self._client = client
        self._settings = settings

    @property
    def name(self) -> str:
        return self._client.post(
            "name", body={"settings": self._settings.model_dump()}
        ).json()

    def get_id_types(self) -> dict[str, list[IdType]]:
        return self._client.post(
            "id-types", body={"settings": self._settings.model_dump()}
        ).json()

    def get_coverage(
        self,
        names: str | list[str] | None = None,
        *,
        by: Literal["date", "asset"] = "date",
        metric: Literal["count", "holding"] = "count",
        stats: list[str] | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {"by": str(by), "metric": str(metric)}
        if stats is not None:
            params["stats"] = stats
        response = self._client.post(
            "coverage",
            params=params,
            body={"names": names, "settings": self._settings.model_dump()},
        )
        if response.status_code == 404:
            raise KeyError(response.json()["detail"])
        elif response.status_code == 400:
            raise ValueError(response.json()["detail"])
        return pl.read_parquet(io.BytesIO(response.content))

    def get_portfolio_names(self) -> list[str]:
        response = self._client.post(
            "names", body={"settings": self._settings.model_dump()}
        )
        return response.json()

    def get_portfolio_groups(self) -> dict[str, list[str]]:
        response = self._client.post(
            "groups", body={"settings": self._settings.model_dump()}
        )
        return response.json()

    def get_dates(
        self, names: list[str] | str | None = None, *, collapse: bool = False
    ) -> dict[str, list[dt.date]]:
        response = self._client.post(
            "dates",
            params={"collapse": collapse},
            body={"names": names, "settings": self._settings.model_dump()},
        )
        response_data = response.json()
        if response.status_code == 404:
            raise KeyError(response_data["detail"])
        elif response.status_code == 400:
            raise ValueError(response_data["detail"])
        return {p: [to_date(d) for d in response_data[p]] for p in response_data.keys()}

    def get_portfolio(
        self,
        names: list[str] | str,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        response = self._client.post(
            "data",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "id_type": id_type,
            },
            body={"names": names, "settings": self._settings.model_dump()},
        )
        if response.status_code == 404:
            raise KeyError(response.json()["detail"])
        elif response.status_code == 400:
            raise ValueError(response.json()["detail"])
        return pl.read_parquet(io.BytesIO(response.content))


class PortfolioParserClientImpl(PortfolioParserApi):

    def __init__(self, client: ApiClient, parser_name: str):
        self._client = client.append_base_path(parser_name)
        self._parser_name = parser_name

    @property
    def name(self) -> str:
        return self._parser_name

    def get_examples(self) -> list[pl.DataFrame]:
        response = self._client.options("")
        result = []
        for bytes in response.iter_bytes():
            result.append(pl.read_parquet(io.BytesIO(bytes)))
        return result

    def can_handle(self, df: pl.DataFrame) -> PortfolioParserResult:
        out = io.BytesIO()
        df.write_parquet(out)
        response = self._client.put("", body=out.getvalue())
        return PortfolioParserResult.model_validate(response.json())

    def parse(self, df: pl.DataFrame) -> tuple[pl.DataFrame, PortfolioParserResult]:
        out = io.BytesIO()
        df.write_parquet(out)
        response = self._client.post("", body=out.getvalue())
        result = PortfolioParserResult.model_validate_json(
            response.headers["X-Metadata"]
        )
        df = pl.read_parquet(io.BytesIO(response.content))
        return df, result


class AsyncPortfolioParserClientImpl(AsyncPortfolioParserApi):

    def __init__(self, client: AsyncApiClient, parser_name: str):
        self._client = client.append_base_path(parser_name)
        self._parser_name = parser_name

    @property
    def name(self) -> str:
        return self._parser_name

    async def get_examples(self) -> list[pl.DataFrame]:
        response = await self._client.options("")
        result = []
        async for bytes in response.aiter_bytes():
            result.append(pl.read_parquet(io.BytesIO(bytes)))
        return result

    async def can_handle(self, df: pl.DataFrame) -> PortfolioParserResult:
        out = io.BytesIO()
        df.write_parquet(out)
        response = await self._client.put("", body=out.getvalue())
        return PortfolioParserResult.model_validate(response.json())

    async def parse(
        self, df: pl.DataFrame
    ) -> tuple[pl.DataFrame, PortfolioParserResult]:
        out = io.BytesIO()
        df.write_parquet(out)
        response = await self._client.post("", body=out.getvalue())
        result = PortfolioParserResult.model_validate_json(
            response.headers["X-Metadata"]
        )
        df = pl.read_parquet(io.BytesIO(response.content))
        return df, result


class PortfolioUploadClientImpl(PortfolioUploadApi):

    def __init__(self, client: ApiClient):
        self._client = client

    def get_parser_result(self) -> PortfolioParserResult:
        return PortfolioParserResult.model_validate(self._client.get("").json())

    def get_raw(self) -> pl.DataFrame:
        return pl.read_parquet(io.BytesIO(self._client.get("raw").content))

    def get_parsed(self) -> pl.DataFrame:
        return pl.read_parquet(io.BytesIO(self._client.get("parsed").content))


class AsyncPortfolioUploadClientImpl(AsyncPortfolioUploadApi):

    def __init__(self, client: AsyncApiClient):
        self._client = client

    async def get_parser_result(self) -> PortfolioParserResult:
        return PortfolioParserResult.model_validate((await self._client.get("")).json())

    async def get_raw(self) -> pl.DataFrame:
        return pl.read_parquet(io.BytesIO((await self._client.get("raw")).content))

    async def get_parsed(self) -> pl.DataFrame:
        return pl.read_parquet(io.BytesIO((await self._client.get("parsed")).content))


class PortfolioUploadLoaderClientImpl(PortfolioUploadLoaderApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("portfolio/uploader")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-upload"),
            PortfolioUploadSettings,
            PortfolioUploadSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[PortfolioUploadSettings, PortfolioUploadSettingsMenu]:
        return self._settings

    def load(
        self,
        ref_or_settings: str | int | PortfolioUploadSettings,
    ) -> PortfolioUploadApi:
        if isinstance(ref_or_settings, PortfolioUploadSettings):
            raise ValueError("Cannot load a portfolio upload with existing reference")
        else:
            settings = self.settings.get(ref_or_settings)

        menu = self.settings.available_settings()
        menu.validate_settings(settings)
        if isinstance(ref_or_settings, int):
            identifier = ref_or_settings
        else:
            identifier = self.settings.names()[ref_or_settings]

        return PortfolioUploadClientImpl(self._client.append_base_path(str(identifier)))

    def get_parser_names(self) -> list[str]:
        return self._client.get("parser").json()

    def get_parser(self, parser: str) -> PortfolioParserApi:
        if parser not in self.get_parser_names():
            raise KeyError(parser)
        return PortfolioParserClientImpl(
            self._client.append_base_path("parser"), parser_name=parser
        )

    def can_handle(
        self, df: pl.DataFrame, *, parser: str | None = None
    ) -> PortfolioParserResult:
        out = io.BytesIO()
        df.write_parquet(out)
        params = {}
        if parser:
            params["parser"] = parser
        response = self._client.put("", body=out.getvalue(), params=params)
        return PortfolioParserResult.model_validate(response.json())

    def upload(
        self, name: str, df: pl.DataFrame, *, parser: str | None = None
    ) -> PortfolioUploadSettings:
        out = io.BytesIO()
        df.write_parquet(out)
        params = {"name": name}
        if parser:
            params["parser"] = parser
        response = self._client.post("", body=out.getvalue(), params=params)
        try:
            response.raise_for_status()
        except Exception as e:
            ppr = PortfolioParserResult.model_validate(response.json()["detail"])
            raise PortfolioUploadError(ppr) from e
        return PortfolioUploadSettings.model_validate(response.json())

    def delete(self, name: str) -> RawSettings:
        response = self._client.delete(name)
        return RawSettings.model_validate(response.json())


class AsyncPortfolioUploadLoaderClientImpl(AsyncPortfolioUploadLoaderApi):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("portfolio/uploader")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-upload"),
            PortfolioUploadSettings,
            PortfolioUploadSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[PortfolioUploadSettings, PortfolioUploadSettingsMenu]:
        return self._settings

    async def load(
        self,
        ref_or_settings: str | int | PortfolioUploadSettings,
    ) -> AsyncPortfolioUploadApi:
        if isinstance(ref_or_settings, PortfolioUploadSettings):
            raise ValueError("Cannot load a portfolio upload with existing reference")
        else:
            settings = await self.settings.get(ref_or_settings)

        menu = await self.settings.available_settings()
        menu.validate_settings(settings)

        if isinstance(ref_or_settings, int):
            identifier = ref_or_settings
        else:
            identifier = (await self.settings.names())[ref_or_settings]

        return AsyncPortfolioUploadClientImpl(
            self._client.append_base_path(str(identifier))
        )

    async def get_parser_names(self) -> list[str]:
        return (await self._client.get("parser")).json()

    async def get_parser(self, parser: str) -> AsyncPortfolioParserApi:
        if parser not in await self.get_parser_names():
            raise KeyError(parser)
        return AsyncPortfolioParserClientImpl(
            self._client.append_base_path("parser"), parser_name=parser
        )

    async def can_handle(
        self, df: pl.DataFrame, *, parser: str | None = None
    ) -> PortfolioParserResult:
        out = io.BytesIO()
        df.write_parquet(out)
        params = {}
        if parser:
            params["parser"] = parser
        response = await self._client.put("", body=out.getvalue(), params=params)
        return PortfolioParserResult.model_validate(response.json())

    async def upload(
        self, name: str, df: pl.DataFrame, *, parser: str | None = None
    ) -> PortfolioUploadSettings:
        out = io.BytesIO()
        df.write_parquet(out)
        params = {"name": name}
        if parser:
            params["parser"] = parser
        response = await self._client.post("", body=out.getvalue(), params=params)
        try:
            response.raise_for_status()
        except Exception as e:
            ppr = PortfolioParserResult.model_validate(response.json()["detail"])
            raise PortfolioUploadError(ppr) from e
        return PortfolioUploadSettings.model_validate(response.json())

    async def delete(self, name: str) -> RawSettings:
        response = await self._client.delete(name)
        return RawSettings.model_validate(response.json())


class AsyncPortfolioLoaderClientImpl(AsyncPortfolioLoaderApi):
    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("portfolio")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio"),
            PortfolioSettings,
            PortfolioSettingsMenu,
        )
        self._uploader = AsyncPortfolioUploadLoaderClientImpl(client)
        self._organizer_settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-organizer"),
            PortfolioOrganizerSettings,
            PortfolioOrganizerSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[PortfolioSettings, PortfolioSettingsMenu]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | PortfolioSettings
    ) -> AsyncPortfolioApi:
        if isinstance(ref_or_settings, PortfolioSettings):
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return AsyncPortfolioClientImpl(self._client, ref_or_settings)
        else:
            portfoliohierarchy_settings = await self.settings.get(ref_or_settings)
            return AsyncPortfolioClientImpl(
                self._client,
                portfoliohierarchy_settings,
            )

    @property
    def uploader(self) -> AsyncPortfolioUploadLoaderApi:
        return self._uploader

    @property
    def organizer_settings(
        self,
    ) -> AsyncSettingsRegistry[
        PortfolioOrganizerSettings, PortfolioOrganizerSettingsMenu
    ]:
        return self._organizer_settings


class PortfolioLoaderClientImpl(PortfolioLoaderApi):
    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("portfolio")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio"),
            PortfolioSettings,
            PortfolioSettingsMenu,
        )
        self._uploader = PortfolioUploadLoaderClientImpl(client)
        self._organizer_settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-organizer"),
            PortfolioOrganizerSettings,
            PortfolioOrganizerSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[PortfolioSettings, PortfolioSettingsMenu]:
        return self._settings

    def load(self, ref_or_settings: str | int | PortfolioSettings) -> PortfolioApi:
        if isinstance(ref_or_settings, PortfolioSettings):
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return PortfolioClientImpl(self._client, ref_or_settings)
        else:
            portfoliohierarchy_settings = self.settings.get(ref_or_settings)
            return PortfolioClientImpl(
                self._client,
                portfoliohierarchy_settings,
            )

    @property
    def uploader(self) -> PortfolioUploadLoaderApi:
        return self._uploader

    @property
    def organizer_settings(
        self,
    ) -> SettingsRegistry[PortfolioOrganizerSettings, PortfolioOrganizerSettingsMenu]:
        return self._organizer_settings
