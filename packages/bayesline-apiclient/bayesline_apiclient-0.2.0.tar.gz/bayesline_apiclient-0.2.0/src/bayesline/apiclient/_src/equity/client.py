import asyncio
import datetime as dt
import importlib.util
import io
from typing import Any, Literal

import polars as pl
from bayesline.api import (
    AsyncSettingsRegistry,
    SettingsRegistry,
)
from bayesline.api.equity import (
    AssetIdApi,
    AsyncAssetIdApi,
    AsyncBayeslineEquityApi,
    AsyncCalendarLoaderApi,
    AsyncExposureApi,
    AsyncExposureLoaderApi,
    AsyncFactorModelApi,
    AsyncFactorModelConstructionApi,
    AsyncFactorModelConstructionLoaderApi,
    AsyncFactorModelEngineApi,
    AsyncFactorModelLoaderApi,
    AsyncPortfolioHierarchyApi,
    AsyncPortfolioHierarchyLoaderApi,
    AsyncPortfolioLoaderApi,
    AsyncReportLoaderApi,
    AsyncUniverseApi,
    AsyncUniverseLoaderApi,
    BayeslineEquityApi,
    CalendarLoaderApi,
    ExposureApi,
    ExposureLoaderApi,
    ExposureSettings,
    ExposureSettingsMenu,
    FactorModelApi,
    FactorModelConstructionApi,
    FactorModelConstructionLoaderApi,
    FactorModelEngineApi,
    FactorModelLoaderApi,
    FactorRiskModelSettings,
    FactorRiskModelSettingsMenu,
    FactorType,
    ModelConstructionSettings,
    ModelConstructionSettingsMenu,
    PortfolioHierarchyApi,
    PortfolioHierarchyLoaderApi,
    PortfolioHierarchySettings,
    PortfolioHierarchySettingsMenu,
    PortfolioLoaderApi,
    ReportLoaderApi,
    UniverseApi,
    UniverseLoaderApi,
    UniverseSettings,
    UniverseSettingsMenu,
)
from bayesline.api.types import (
    DateLike,
    IdType,
    to_date,
    to_date_string,
)

from bayesline.apiclient._src.client import ApiClient, AsyncApiClient
from bayesline.apiclient._src.equity.calendar import (
    AsyncCalendarLoaderClientImpl,
    CalendarLoaderClientImpl,
)
from bayesline.apiclient._src.equity.portfolio import (
    AsyncPortfolioLoaderClientImpl,
    PortfolioLoaderClientImpl,
)
from bayesline.apiclient._src.equity.portfolioreport import (
    AsyncReportLoaderClientImpl,
    ReportLoaderClientImpl,
)
from bayesline.apiclient._src.settings import (
    AsyncHttpSettingsRegistryClient,
    HttpSettingsRegistryClient,
)

tqdm = lambda x: x  # noqa: E731
if importlib.util.find_spec("tqdm"):
    from tqdm import tqdm  # type: ignore


class AssetIdClientImpl(AssetIdApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("ids")

    def lookup_ids(self, ids: list[str], top_n: int = 0) -> pl.DataFrame:
        response = self._client.get("lookup", params={"ids": ids, "top_n": top_n})
        try:
            response.raise_for_status()
        except Exception as e:
            raise ValueError(response.json()["detail"]) from e
        return pl.read_parquet(io.BytesIO(response.content))


class AsyncAssetIdClientImpl(AsyncAssetIdApi):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("ids")

    async def lookup_ids(self, ids: list[str], top_n: int = 0) -> pl.DataFrame:
        response = await self._client.get("lookup", params={"ids": ids, "top_n": top_n})
        try:
            response.raise_for_status()
        except Exception as e:
            raise ValueError(response.json()["detail"]) from e
        return pl.read_parquet(io.BytesIO(response.content))


class UniverseClientImpl(UniverseApi):

    def __init__(
        self,
        client: ApiClient,
        universe_settings: UniverseSettings,
        id_types: list[IdType],
    ):
        self._client = client
        self._universe_settings = universe_settings
        self._id_types = id_types

    @property
    def settings(self) -> UniverseSettings:
        return self._universe_settings

    @property
    def id_types(self) -> list[IdType]:
        return list(self._id_types)

    def coverage(self, id_type: IdType | None = None) -> list[str]:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)

        response = self._client.post(
            "coverage",
            params=params,
            body=self._universe_settings.model_dump(),
        )

        return response.json()

    def dates(
        self, *, range_only: bool = False, trade_only: bool = False
    ) -> list[dt.date]:
        response = self._client.post(
            "dates",
            params={"range_only": range_only, "trade_only": trade_only},
            body=self._universe_settings.model_dump(),
        )
        return [to_date(d) for d in response.json()]

    def input_id_mapping(
        self,
        *,
        id_type: IdType | None = None,
        filter_mode: Literal["all", "mapped", "unmapped"] = "all",
        mode: Literal[
            "all", "daily-counts", "input-asset-counts", "latest-name"
        ] = "all",
    ) -> pl.DataFrame:
        params: dict[str, Any] = {
            "mode": mode,
            "filter_mode": filter_mode,
        }
        _check_and_add_id_type(self._id_types, id_type, params)
        response = self._client.post(
            "input-id-mapping",
            params=params,
            body=self._universe_settings.model_dump(),
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def counts(
        self,
        dates: bool = True,
        industry_level: int = 0,
        region_level: int = 0,
        universe_type: Literal["estimation", "coverage", "both"] = "both",
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)
        params["dates"] = dates
        params["industry_level"] = industry_level
        params["region_level"] = region_level
        params["universe_type"] = universe_type

        response = self._client.post(
            "counts",
            params=params,
            body=self._universe_settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))

    def get(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)

        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        params["filter_tradedays"] = filter_tradedays

        response = self._client.post(
            "",
            params=params,
            body=self._universe_settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))


class AsyncUniverseClientImpl(AsyncUniverseApi):

    def __init__(
        self,
        client: AsyncApiClient,
        universe_settings: UniverseSettings,
        id_types: list[IdType],
    ):
        self._client = client
        self._universe_settings = universe_settings
        self._id_types = id_types

    @property
    def settings(self) -> UniverseSettings:
        return self._universe_settings

    @property
    def id_types(self) -> list[IdType]:
        return list(self._id_types)

    async def coverage(self, id_type: IdType | None = None) -> list[str]:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)

        response = await self._client.post(
            "coverage",
            params=params,
            body=self._universe_settings.model_dump(),
        )

        return response.json()

    async def dates(
        self, *, range_only: bool = False, trade_only: bool = False
    ) -> list[dt.date]:
        response = await self._client.post(
            "dates",
            params={"range_only": range_only, "trade_only": trade_only},
            body=self._universe_settings.model_dump(),
        )
        return [to_date(d) for d in response.json()]

    async def input_id_mapping(
        self,
        *,
        id_type: IdType | None = None,
        filter_mode: Literal["all", "mapped", "unmapped"] = "all",
        mode: Literal[
            "all", "daily-counts", "input-asset-counts", "latest-name"
        ] = "all",
    ) -> pl.DataFrame:
        params: dict[str, Any] = {
            "mode": mode,
            "filter_mode": filter_mode,
        }
        _check_and_add_id_type(self._id_types, id_type, params)
        response = await self._client.post(
            "input-id-mapping",
            params=params,
            body=self._universe_settings.model_dump(),
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def counts(
        self,
        dates: bool = True,
        industry_level: int = 0,
        region_level: int = 0,
        universe_type: Literal["estimation", "coverage", "both"] = "both",
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)
        params["dates"] = dates
        params["industry_level"] = industry_level
        params["region_level"] = region_level
        params["universe_type"] = universe_type

        response = await self._client.post(
            "counts",
            params=params,
            body=self._universe_settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))

    async def get(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)

        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        params["filter_tradedays"] = filter_tradedays

        response = await self._client.post(
            "",
            params=params,
            body=self._universe_settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))


class UniverseLoaderClientImpl(UniverseLoaderApi):
    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("universe")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/universe"),
            UniverseSettings,
            UniverseSettingsMenu,
        )

    @property
    def settings(self) -> SettingsRegistry[UniverseSettings, UniverseSettingsMenu]:
        return self._settings

    def load(self, ref_or_settings: str | int | UniverseSettings) -> UniverseApi:
        id_types = self._settings.available_settings().id_types

        if isinstance(ref_or_settings, UniverseSettings):
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return UniverseClientImpl(self._client, ref_or_settings, id_types)
        else:
            universe_settings = self.settings.get(ref_or_settings)
            return UniverseClientImpl(self._client, universe_settings, id_types)


class AsyncUniverseLoaderClientImpl(AsyncUniverseLoaderApi):
    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("universe")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/universe"),
            UniverseSettings,
            UniverseSettingsMenu,
        )

    @property
    def settings(self) -> AsyncSettingsRegistry[UniverseSettings, UniverseSettingsMenu]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | UniverseSettings
    ) -> AsyncUniverseApi:
        settings_menu = await self._settings.available_settings()
        id_types = settings_menu.id_types

        if isinstance(ref_or_settings, UniverseSettings):
            settings_menu.validate_settings(ref_or_settings)
            return AsyncUniverseClientImpl(self._client, ref_or_settings, id_types)
        else:
            universe_settings = await self.settings.get(ref_or_settings)
            return AsyncUniverseClientImpl(self._client, universe_settings, id_types)


class ExposureClientImpl(ExposureApi):

    def __init__(
        self,
        client: ApiClient,
        exposure_settings: ExposureSettings,
        id_types: list[IdType],
        universe_api: UniverseLoaderApi,
    ):
        self._client = client
        self._exposure_settings = exposure_settings
        self._id_types = id_types
        self._universe_api = universe_api

    @property
    def settings(self) -> ExposureSettings:
        return self._exposure_settings

    def dates(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        range_only: bool = False,
    ) -> list[dt.date]:
        if isinstance(universe, str | int):
            universe_settings = self._universe_api.settings.get(universe)
        elif isinstance(universe, UniverseSettings):
            universe_settings = universe
        elif isinstance(universe, UniverseApi):
            universe_settings = universe.settings
        else:
            raise ValueError(f"illegal universe input {universe}")

        response = self._client.post(
            "dates",
            params={"range_only": range_only},
            body={
                "universe_settings": universe_settings.model_dump(),
                "exposure_settings": self._exposure_settings.model_dump(),
            },
        )
        return [to_date(d) for d in response.json()]

    def coverage_stats(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        id_type: IdType | None = None,
        by: Literal["date", "asset"] = "date",
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)
        params["by"] = by

        if isinstance(universe, str | int):
            universe_settings = self._universe_api.settings.get(universe)
        elif isinstance(universe, UniverseSettings):
            universe_settings = universe
        elif isinstance(universe, AsyncUniverseApi):
            universe_settings = universe.settings
        else:
            raise ValueError(f"illegal universe input {universe}")

        response = self._client.post(
            "/coverage-stats",
            params=params,
            body={
                "universe_settings": universe_settings.model_dump(),
                "exposure_settings": self._exposure_settings.model_dump(),
            },
        )
        response.raise_for_status()
        return pl.read_parquet(io.BytesIO(response.content))

    def get(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)

        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        params["filter_tradedays"] = filter_tradedays

        if isinstance(universe, str | int):
            universe_settings = self._universe_api.settings.get(universe)
        elif isinstance(universe, UniverseSettings):
            universe_settings = universe
        elif isinstance(universe, UniverseApi):
            universe_settings = universe.settings
        else:
            raise ValueError(f"illegal universe input {universe}")

        body = {
            "universe_settings": universe_settings.model_dump(),
            "exposure_settings": self._exposure_settings.model_dump(),
        }

        response = self._client.post(
            "",
            params=params,
            body=body,
        )

        def _read_df(r: Any) -> pl.DataFrame:
            return pl.read_parquet(io.BytesIO(r.content))

        if response.headers["content-type"] == "application/json":
            df = pl.concat(
                _read_df(self._client.post(page, body=body, absolute_url=True))
                for page in tqdm(response.json()["urls"])
            )
        else:
            df = _read_df(response)

        return df


class AsyncExposureClientImpl(AsyncExposureApi):

    def __init__(
        self,
        client: AsyncApiClient,
        exposure_settings: ExposureSettings,
        id_types: list[IdType],
        universe_api: AsyncUniverseLoaderApi,
    ):
        self._client = client
        self._exposure_settings = exposure_settings
        self._id_types = id_types
        self._universe_api = universe_api

    @property
    def settings(self) -> ExposureSettings:
        return self._exposure_settings

    async def dates(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        range_only: bool = False,
    ) -> list[dt.date]:
        if isinstance(universe, str | int):
            universe_settings = await self._universe_api.settings.get(universe)
        elif isinstance(universe, UniverseSettings):
            universe_settings = universe
        elif isinstance(universe, AsyncUniverseApi):
            universe_settings = universe.settings
        else:
            raise ValueError(f"illegal universe input {universe}")

        response = await self._client.post(
            "dates",
            params={"range_only": range_only},
            body={
                "universe_settings": universe_settings.model_dump(),
                "exposure_settings": self._exposure_settings.model_dump(),
            },
        )
        return [to_date(d) for d in response.json()]

    async def coverage_stats(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        id_type: IdType | None = None,
        by: Literal["date", "asset"] = "date",
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)
        params["by"] = by

        if isinstance(universe, str | int):
            universe_settings = await self._universe_api.settings.get(universe)
        elif isinstance(universe, UniverseSettings):
            universe_settings = universe
        elif isinstance(universe, AsyncUniverseApi):
            universe_settings = universe.settings
        else:
            raise ValueError(f"illegal universe input {universe}")

        response = await self._client.post(
            "/coverage-stats",
            params=params,
            body={
                "universe_settings": universe_settings.model_dump(),
                "exposure_settings": self._exposure_settings.model_dump(),
            },
        )
        response.raise_for_status()
        return pl.read_parquet(io.BytesIO(response.content))

    async def get(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        _check_and_add_id_type(self._id_types, id_type, params)

        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        params["filter_tradedays"] = filter_tradedays

        if isinstance(universe, str | int):
            universe_settings = await self._universe_api.settings.get(universe)
        elif isinstance(universe, UniverseSettings):
            universe_settings = universe
        elif isinstance(universe, UniverseApi):
            universe_settings = universe.settings
        else:
            raise ValueError(f"illegal universe input {universe}")

        body = {
            "universe_settings": universe_settings.model_dump(),
            "exposure_settings": self._exposure_settings.model_dump(),
        }

        response = await self._client.post(
            "",
            params=params,
            body=body,
        )

        def _read_df(r: Any) -> pl.DataFrame:
            return pl.read_parquet(io.BytesIO(r.content))

        if response.headers["content-type"] == "application/json":
            tasks = []
            pages = response.json()["urls"]
            results = []
            tasks = [
                self._client.post(page, body=body, absolute_url=True) for page in pages
            ]
            results.extend(await asyncio.gather(*tasks))

            df = pl.concat(_read_df(r) for r in results)
        else:
            df = _read_df(response)

        return df


class ExposureLoaderClientImpl(ExposureLoaderApi):

    def __init__(
        self,
        client: ApiClient,
        universe_api: UniverseLoaderApi,
    ):
        self._client = client.append_base_path("exposures")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/exposure"),
            ExposureSettings,
            ExposureSettingsMenu,
        )
        self._universe_api = universe_api

    @property
    def settings(self) -> SettingsRegistry[ExposureSettings, ExposureSettingsMenu]:
        return self._settings

    def load(self, ref_or_settings: str | int | ExposureSettings) -> ExposureApi:
        id_types = self._universe_api.settings.available_settings().id_types

        if isinstance(ref_or_settings, ExposureSettings):
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return ExposureClientImpl(
                self._client,
                ref_or_settings,
                id_types,
                self._universe_api,
            )
        else:
            exposure_settings = self.settings.get(ref_or_settings)
            return ExposureClientImpl(
                self._client,
                exposure_settings,
                id_types,
                self._universe_api,
            )


class AsyncExposureLoaderClientImpl(AsyncExposureLoaderApi):

    def __init__(
        self,
        client: AsyncApiClient,
        universe_api: AsyncUniverseLoaderApi,
    ):
        self._client = client.append_base_path("exposures")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/exposure"),
            ExposureSettings,
            ExposureSettingsMenu,
        )
        self._universe_api = universe_api

    @property
    def settings(self) -> AsyncSettingsRegistry[ExposureSettings, ExposureSettingsMenu]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | ExposureSettings
    ) -> AsyncExposureApi:
        id_types = (await self._universe_api.settings.available_settings()).id_types

        if isinstance(ref_or_settings, ExposureSettings):
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return AsyncExposureClientImpl(
                self._client,
                ref_or_settings,
                id_types,
                self._universe_api,
            )
        else:
            exposure_settings = await self.settings.get(ref_or_settings)
            return AsyncExposureClientImpl(
                self._client,
                exposure_settings,
                id_types,
                self._universe_api,
            )


class FactorModelClientImpl(FactorModelApi):

    def __init__(
        self,
        client: ApiClient,
        model_id: int,
        settings: FactorRiskModelSettings,
    ):
        self._client = client
        self._model_id = model_id
        self._settings = settings

    def dates(self) -> list[dt.date]:
        response = self._client.get(f"model/{self._model_id}/dates")
        return [to_date(d) for d in response.json()]

    def factors(self, *which: FactorType) -> list[str]:
        response = self._client.get(
            f"model/{self._model_id}/factors",
            params={"which": list(which)},
        )
        return response.json()

    def exposures(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        params = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(f"model/{self._model_id}/exposures", params=params)
        return pl.read_parquet(io.BytesIO(response.content))

    def universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        params = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(f"model/{self._model_id}/universe", params=params)
        return pl.read_parquet(io.BytesIO(response.content))

    def estimation_universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        params = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(
            f"model/{self._model_id}/estimation-universe", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def market_caps(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(
            f"model/{self._model_id}/market-caps", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def weights(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(f"model/{self._model_id}/weights", params=params)
        return pl.read_parquet(io.BytesIO(response.content))

    def future_asset_returns(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(
            f"model/{self._model_id}/future-asset-returns", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def t_stats(self) -> pl.DataFrame:
        response = self._client.get(f"model/{self._model_id}/t-stats")
        return pl.read_parquet(io.BytesIO(response.content))

    def p_values(self) -> pl.DataFrame:
        response = self._client.get(f"model/{self._model_id}/p-values")
        return pl.read_parquet(io.BytesIO(response.content))

    def r2(self) -> pl.DataFrame:
        response = self._client.get(f"model/{self._model_id}/r2")
        return pl.read_parquet(io.BytesIO(response.content))

    def sigma2(self) -> pl.DataFrame:
        response = self._client.get(f"model/{self._model_id}/sigma2")
        return pl.read_parquet(io.BytesIO(response.content))

    def style_correlation(
        self, start: DateLike | None = None, end: DateLike | None = None
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = self._client.get(
            f"model/{self._model_id}/style-correlation",
            params=params,
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def industry_exposures(
        self, start: DateLike | None = None, end: DateLike | None = None
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = self._client.get(
            f"model/{self._model_id}/industry-exposures",
            params=params,
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def fcov(
        self,
        start: DateLike | int | None = -1,
        end: DateLike | int | None = None,
        dates: list[DateLike] | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start is not None:
            if not isinstance(start, int):
                params["start"] = to_date_string(start)
            else:
                params["start"] = start  # type: ignore

        if end is not None:
            if not isinstance(end, int):
                params["end"] = to_date_string(end)
            else:
                params["end"] = end  # type: ignore

        body = {"dates": None}
        if dates is not None:
            body["dates"] = [to_date_string(d) for d in dates]  # type: ignore

        response = self._client.post(
            f"model/{self._model_id}/fcov", params=params, body=body
        )
        return pl.read_parquet(io.BytesIO(response.content))

    def fret(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if freq is not None:
            params["freq"] = freq
        if cumulative:
            params["cumulative"] = cumulative
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = self._client.get(
            f"model/{self._model_id}/fret",
            params=params,
        )
        return pl.read_parquet(io.BytesIO(response.content))


class AsyncFactorModelClientImpl(AsyncFactorModelApi):

    def __init__(
        self,
        client: AsyncApiClient,
        model_id: int,
        settings: FactorRiskModelSettings,
    ):
        self._client = client
        self._model_id = model_id
        self._settings = settings

    async def dates(self) -> list[dt.date]:
        response = await self._client.get(f"model/{self._model_id}/dates")
        return [to_date(d) for d in response.json()]

    async def factors(self, *which: FactorType) -> list[str]:
        response = await self._client.get(
            f"model/{self._model_id}/factors",
            params={"which": list(which)},
        )
        return response.json()

    async def exposures(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        params = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/exposures", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        params = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/universe", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def estimation_universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        params = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/estimation-universe", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def market_caps(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/market-caps", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def weights(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/weights", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def future_asset_returns(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/future-asset-returns", params=params
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def t_stats(self) -> pl.DataFrame:
        response = await self._client.get(f"model/{self._model_id}/t-stats")
        return pl.read_parquet(io.BytesIO(response.content))

    async def p_values(self) -> pl.DataFrame:
        response = await self._client.get(f"model/{self._model_id}/p-values")
        return pl.read_parquet(io.BytesIO(response.content))

    async def r2(self) -> pl.DataFrame:
        response = await self._client.get(f"model/{self._model_id}/r2")
        return pl.read_parquet(io.BytesIO(response.content))

    async def sigma2(self) -> pl.DataFrame:
        response = await self._client.get(f"model/{self._model_id}/sigma2")
        return pl.read_parquet(io.BytesIO(response.content))

    async def style_correlation(
        self, start: DateLike | None = None, end: DateLike | None = None
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = await self._client.get(
            f"model/{self._model_id}/style-correlation",
            params=params,
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def industry_exposures(
        self, start: DateLike | None = None, end: DateLike | None = None
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = await self._client.get(
            f"model/{self._model_id}/industry-exposures",
            params=params,
        )
        return pl.read_parquet(io.BytesIO(response.content))

    async def fret(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if freq is not None:
            params["freq"] = freq
        if cumulative:
            params["cumulative"] = cumulative
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = await self._client.get(
            f"model/{self._model_id}/fret",
            params=params,
        )
        return pl.read_parquet(io.BytesIO(response.content))


class FactorModelConstructionClientImpl(FactorModelConstructionApi):

    def __init__(
        self,
        client: ApiClient,
        settings: ModelConstructionSettings,
    ):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> ModelConstructionSettings:
        return self._settings


class AsyncFactorModelConstructionClientImpl(AsyncFactorModelConstructionApi):

    def __init__(
        self,
        client: AsyncApiClient,
        settings: ModelConstructionSettings,
    ):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> ModelConstructionSettings:
        return self._settings


class FactorModelEngineClientImpl(FactorModelEngineApi):

    def __init__(
        self,
        client: ApiClient,
        settings: FactorRiskModelSettings,
        model_id: int | None = None,
    ):
        self._client = client
        self._settings = settings
        self._model_id = model_id

    @property
    def settings(self) -> FactorRiskModelSettings:
        return self._settings

    def get(self) -> FactorModelApi:
        if self._model_id is None:
            self._model_id = self._client.post(
                "model", body=self._settings.model_dump()
            ).json()

        return FactorModelClientImpl(self._client, self._model_id, self._settings)


class AsyncFactorModelEngineClientImpl(AsyncFactorModelEngineApi):

    def __init__(
        self,
        client: AsyncApiClient,
        settings: FactorRiskModelSettings,
        model_id: int | None = None,
    ):
        self._client = client
        self._settings = settings
        self._model_id = model_id

    @property
    def settings(self) -> FactorRiskModelSettings:
        return self._settings

    async def get(self) -> AsyncFactorModelApi:
        if self._model_id is None:
            self._model_id = (
                await self._client.post("model", body=self._settings.model_dump())
            ).json()

        return AsyncFactorModelClientImpl(self._client, self._model_id, self._settings)


class FactorModelConstructionLoaderClientImpl(FactorModelConstructionLoaderApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("modelconstruction")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/model-construction"),
            ModelConstructionSettings,
            ModelConstructionSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[ModelConstructionSettings, ModelConstructionSettingsMenu]:
        return self._settings

    def load(
        self, ref_or_settings: str | int | ModelConstructionSettings
    ) -> FactorModelConstructionApi:
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(settings)
            return FactorModelConstructionClientImpl(self._client, settings)
        else:
            ref = ref_or_settings
            settings_obj = self.settings.get(ref)
            ref = ref_or_settings
            settings_obj = self.settings.get(ref)
            return FactorModelConstructionClientImpl(self._client, settings_obj)


class AsyncFactorModelConstructionLoaderClientImpl(
    AsyncFactorModelConstructionLoaderApi
):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("modelconstruction")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/model-construction"),
            ModelConstructionSettings,
            ModelConstructionSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[
        ModelConstructionSettings, ModelConstructionSettingsMenu
    ]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | ModelConstructionSettings
    ) -> AsyncFactorModelConstructionApi:
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(settings)
            return AsyncFactorModelConstructionClientImpl(self._client, settings)
        else:
            ref = ref_or_settings
            settings_obj = await self.settings.get(ref)
            return AsyncFactorModelConstructionClientImpl(self._client, settings_obj)


class FactorModelLoaderClientImpl(FactorModelLoaderApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("riskmodels")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/factor-risk-model"),
            FactorRiskModelSettings,
            FactorRiskModelSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[FactorRiskModelSettings, FactorRiskModelSettingsMenu]:
        return self._settings

    def load(
        self, ref_or_settings: str | int | FactorRiskModelSettings
    ) -> FactorModelEngineApi:
        if isinstance(ref_or_settings, FactorRiskModelSettings):
            settings = ref_or_settings
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(settings)
            return FactorModelEngineClientImpl(self._client, settings)
        else:
            ref = ref_or_settings
            settings_obj = self.settings.get(ref)
            if isinstance(ref, str):
                model_id = self.settings.names()[ref]
            else:
                model_id = ref
            return FactorModelEngineClientImpl(self._client, settings_obj, model_id)


class AsyncFactorModelLoaderClientImpl(AsyncFactorModelLoaderApi):

    def __init__(
        self,
        client: AsyncApiClient,
    ):
        self._client = client.append_base_path("riskmodels")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/factor-risk-model"),
            FactorRiskModelSettings,
            FactorRiskModelSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[FactorRiskModelSettings, FactorRiskModelSettingsMenu]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | FactorRiskModelSettings
    ) -> AsyncFactorModelEngineApi:
        if isinstance(ref_or_settings, FactorRiskModelSettings):
            settings = ref_or_settings
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(settings)
            return AsyncFactorModelEngineClientImpl(self._client, settings)
        else:
            ref = ref_or_settings
            settings_obj = await self.settings.get(ref)
            if isinstance(ref, str):
                names = await self.settings.names()
                model_id = names[ref]
            else:
                model_id = ref
            return AsyncFactorModelEngineClientImpl(
                self._client, settings_obj, model_id
            )


class PortfolioHierarchyClientImpl(PortfolioHierarchyApi):

    def __init__(self, client: ApiClient, settings: PortfolioHierarchySettings):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> PortfolioHierarchySettings:
        return self._settings

    def get_id_types(self) -> dict[str, list[IdType]]:
        return self._client.post("id-types", body=self._settings.model_dump()).json()

    def get_dates(self, *, collapse: bool = False) -> dict[str, list[dt.date]]:
        response = self._client.post(
            "dates", body=self._settings.model_dump(), params={"collapse": collapse}
        )
        response_data = response.json()
        return {p: [to_date(d) for d in response_data[p]] for p in response_data.keys()}

    def get(
        self,
        start_date: DateLike | None,
        end_date: DateLike | None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start_date is not None:
            params["start_date"] = to_date_string(start_date)
        if end_date is not None:
            params["end_date"] = to_date_string(end_date)
        if id_type is not None:
            params["id_type"] = id_type
        response = self._client.post(
            "/",
            params=params,
            body=self._settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))


class AsyncPortfolioHierarchyClientImpl(AsyncPortfolioHierarchyApi):

    def __init__(self, client: AsyncApiClient, settings: PortfolioHierarchySettings):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> PortfolioHierarchySettings:
        return self._settings

    async def get_id_types(self) -> dict[str, list[IdType]]:
        return (
            await self._client.post("id-types", body=self._settings.model_dump())
        ).json()

    async def get_dates(self, *, collapse: bool = False) -> dict[str, list[dt.date]]:
        response = await self._client.post(
            "dates", body=self._settings.model_dump(), params={"collapse": collapse}
        )
        response_data = response.json()
        return {p: [to_date(d) for d in response_data[p]] for p in response_data.keys()}

    async def get(
        self,
        start_date: DateLike | None,
        end_date: DateLike | None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params = {}
        if start_date is not None:
            params["start_date"] = to_date_string(start_date)
        if end_date is not None:
            params["end_date"] = to_date_string(end_date)
        if id_type is not None:
            params["id_type"] = id_type
        response = await self._client.post(
            "/",
            params=params,
            body=self._settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))


class PortfolioHierarchyLoaderClientImpl(PortfolioHierarchyLoaderApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("portfoliohierarchy")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-hierarchy"),
            PortfolioHierarchySettings,
            PortfolioHierarchySettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[PortfolioHierarchySettings, PortfolioHierarchySettingsMenu]:
        return self._settings

    def load(
        self, ref_or_settings: str | int | PortfolioHierarchySettings
    ) -> PortfolioHierarchyApi:
        if isinstance(ref_or_settings, PortfolioHierarchySettings):
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return PortfolioHierarchyClientImpl(self._client, ref_or_settings)
        else:
            portfoliohierarchy_settings = self.settings.get(ref_or_settings)
            return PortfolioHierarchyClientImpl(
                self._client,
                portfoliohierarchy_settings,
            )


class AsyncPortfolioHierarchyLoaderClientImpl(AsyncPortfolioHierarchyLoaderApi):
    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("portfoliohierarchy")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-hierarchy"),
            PortfolioHierarchySettings,
            PortfolioHierarchySettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[
        PortfolioHierarchySettings, PortfolioHierarchySettingsMenu
    ]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | PortfolioHierarchySettings
    ) -> AsyncPortfolioHierarchyApi:
        if isinstance(ref_or_settings, PortfolioHierarchySettings):
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return AsyncPortfolioHierarchyClientImpl(self._client, ref_or_settings)
        else:
            portfoliohierarchy_settings = await self.settings.get(ref_or_settings)
            return AsyncPortfolioHierarchyClientImpl(
                self._client,
                portfoliohierarchy_settings,
            )


class BayeslineEquityApiClient(BayeslineEquityApi):
    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("equity")
        self._id_client = AssetIdClientImpl(self._client)
        self._calendar_client = CalendarLoaderClientImpl(self._client)
        self._universe_client = UniverseLoaderClientImpl(self._client)
        self._exposure_client = ExposureLoaderClientImpl(
            self._client, self._universe_client
        )
        self._modelconstruction_client = FactorModelConstructionLoaderClientImpl(
            self._client
        )
        self._factorrisk_client = FactorModelLoaderClientImpl(self._client)
        self._portfoliohierarchy_client = PortfolioHierarchyLoaderClientImpl(
            self._client
        )
        self._portfolioreport_client = ReportLoaderClientImpl(
            self._client,
            self._portfoliohierarchy_client,
        )
        self._portfolio_client = PortfolioLoaderClientImpl(self._client)

    @property
    def ids(self) -> AssetIdApi:
        return self._id_client

    @property
    def calendars(self) -> CalendarLoaderApi:
        return self._calendar_client

    @property
    def universes(self) -> UniverseLoaderApi:
        return self._universe_client

    @property
    def exposures(self) -> ExposureLoaderApi:
        return self._exposure_client

    @property
    def modelconstruction(self) -> FactorModelConstructionLoaderApi:
        return self._modelconstruction_client

    @property
    def riskmodels(self) -> FactorModelLoaderApi:
        return self._factorrisk_client

    @property
    def portfolioreport(self) -> ReportLoaderApi:
        return self._portfolioreport_client

    @property
    def portfolios(self) -> PortfolioLoaderApi:
        return self._portfolio_client

    @property
    def portfoliohierarchy(self) -> PortfolioHierarchyLoaderApi:
        return self._portfoliohierarchy_client


class AsyncBayeslineEquityApiClient(AsyncBayeslineEquityApi):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("equity")
        self._id_client = AsyncAssetIdClientImpl(self._client)
        self._calendar_client = AsyncCalendarLoaderClientImpl(self._client)
        self._universe_client = AsyncUniverseLoaderClientImpl(self._client)

        self._exposure_client = AsyncExposureLoaderClientImpl(
            self._client, self._universe_client
        )
        self._modelconstruction_client = AsyncFactorModelConstructionLoaderClientImpl(
            self._client
        )
        self._factorrisk_client = AsyncFactorModelLoaderClientImpl(self._client)
        self._portfoliohierarchy_client = AsyncPortfolioHierarchyLoaderClientImpl(
            self._client
        )
        self._portfolioreport_client = AsyncReportLoaderClientImpl(
            self._client,
            self._portfoliohierarchy_client,
        )
        self._portfolio_client = AsyncPortfolioLoaderClientImpl(self._client)

    @property
    def ids(self) -> AsyncAssetIdApi:
        return self._id_client

    @property
    def calendars(self) -> AsyncCalendarLoaderApi:
        return self._calendar_client

    @property
    def universes(self) -> AsyncUniverseLoaderApi:
        return self._universe_client

    @property
    def exposures(self) -> AsyncExposureLoaderApi:
        return self._exposure_client

    @property
    def modelconstruction(self) -> AsyncFactorModelConstructionLoaderApi:
        return self._modelconstruction_client

    @property
    def riskmodels(self) -> AsyncFactorModelLoaderApi:
        return self._factorrisk_client

    @property
    def portfolioreport(self) -> AsyncReportLoaderApi:
        return self._portfolioreport_client

    @property
    def portfolios(self) -> AsyncPortfolioLoaderApi:
        return self._portfolio_client

    @property
    def portfoliohierarchy(self) -> AsyncPortfolioHierarchyLoaderApi:
        return self._portfoliohierarchy_client


def _check_and_add_id_type(
    id_types: list[IdType],
    id_type: IdType | None,
    params: dict[str, Any],
) -> None:
    if id_type is not None:
        if id_type not in id_types:
            raise ValueError(f"given id type {id_type} is not supported")
        params["id_type"] = id_type
