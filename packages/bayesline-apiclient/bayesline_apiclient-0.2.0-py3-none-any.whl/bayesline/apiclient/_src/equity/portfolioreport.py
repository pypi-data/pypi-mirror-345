import datetime as dt
import io
from typing import Any

import polars as pl
from bayesline.api import (
    AsyncReadOnlyRegistry,
    AsyncSettingsRegistry,
    ReadOnlyRegistry,
    SettingsMenu,
    SettingsRegistry,
)
from bayesline.api.equity import (
    AsyncPortfolioHierarchyLoaderApi,
    AsyncReportAccessorApi,
    AsyncReportApi,
    AsyncReportLoaderApi,
    AsyncReportPersister,
    IllegalPathError,
    PortfolioHierarchyLoaderApi,
    PortfolioHierarchySettings,
    ReportAccessorApi,
    ReportAccessorSettings,
    ReportApi,
    ReportLoaderApi,
    ReportPersister,
    ReportSettings,
    ReportSettingsMenu,
)
from bayesline.api.types import (
    DateLike,
    DNFFilterExpressions,
    to_date,
    to_date_string,
    to_maybe_date_string,
)

from bayesline.apiclient._src.client import ApiClient, AsyncApiClient
from bayesline.apiclient._src.settings import (
    AsyncHttpSettingsRegistryClient,
    HttpSettingsRegistryClient,
)


def _make_params_dict(**kwargs: Any) -> dict[str, Any]:
    """Remove None values from kwargs and return as dict."""
    return {k: v for k, v in kwargs.items() if v is not None}


class ReportAccessorClientImpl(ReportAccessorApi):

    def __init__(
        self,
        client: ApiClient,
        identifier: int,
        settings: ReportAccessorSettings,
        persister: ReportPersister,
    ) -> None:
        self._client = client
        self._identifier = identifier
        self._settings = settings
        self._persister = persister

    @property
    def identifier(self) -> int:
        return self._identifier

    @property
    def axes(self) -> dict[str, list[str]]:
        return self._settings.axes

    @property
    def metric_cols(self) -> list[str]:
        return self._settings.metric_cols

    @property
    def pivot_cols(self) -> list[str]:
        return self._settings.pivot_cols

    def get_level_values(
        self,
        levels: tuple[str, ...] = (),
        include_totals: bool = False,
        filters: DNFFilterExpressions | None = None,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/levels"
        response = self._client.post(
            url,
            body={
                "levels": levels,
                "include_totals": include_totals,
                "filters": filters,
                "axes": self._settings.axes,
                "metric_cols": self._settings.metric_cols,
            },
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get levels {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    def get_data(
        self,
        path: list[tuple[str, str]],
        *,
        expand: tuple[str, ...] = (),
        pivot_cols: tuple[str, ...] = (),
        value_cols: tuple[str, ...] = (),
        filters: DNFFilterExpressions | None = None,
        pivot_total: bool = False,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/data"
        response = self._client.post(
            url,
            body={
                "path": path,
                "expand": expand,
                "pivot_cols": pivot_cols,
                "value_cols": value_cols,
                "filters": filters,
                "pivot_total": pivot_total,
            },
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get report {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    def persist(self, name: str) -> int:
        return self._persister.persist(name, self._settings, [self])


class AsyncReportAccessorClientImpl(AsyncReportAccessorApi):

    def __init__(
        self,
        client: AsyncApiClient,
        identifier: int,
        settings: ReportAccessorSettings,
        persister: AsyncReportPersister,
    ) -> None:
        self._client = client
        self._identifier = identifier
        self._settings = settings
        self._persister = persister

    @property
    def identifier(self) -> int:
        return self._identifier

    @property
    def axes(self) -> dict[str, list[str]]:
        return self._settings.axes

    @property
    def metric_cols(self) -> list[str]:
        return self._settings.metric_cols

    @property
    def pivot_cols(self) -> list[str]:
        return self._settings.pivot_cols

    async def get_level_values(
        self,
        levels: tuple[str, ...] = (),
        include_totals: bool = False,
        filters: DNFFilterExpressions | None = None,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/levels"
        response = await self._client.post(
            url,
            body={
                "levels": levels,
                "include_totals": include_totals,
                "filters": filters,
                "axes": self._settings.axes,
                "metric_cols": self._settings.metric_cols,
            },
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get levels {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    async def get_data(
        self,
        path: list[tuple[str, str]],
        *,
        expand: tuple[str, ...] = (),
        pivot_cols: tuple[str, ...] = (),
        value_cols: tuple[str, ...] = (),
        filters: DNFFilterExpressions | None = None,
        pivot_total: bool = False,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/data"
        response = await self._client.post(
            url,
            body={
                "path": path,
                "expand": expand,
                "pivot_cols": pivot_cols,
                "value_cols": value_cols,
                "filters": filters,
                "pivot_total": pivot_total,
            },
        )

        if response.status_code == 400:
            raise IllegalPathError(response.json()["detail"])

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get report {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    async def persist(self, name: str) -> int:
        return await self._persister.persist(name, self._settings, [self])


class ReportClientImpl(ReportApi):

    def __init__(
        self,
        client: ApiClient,
        report_id: str,
        settings: ReportSettings,
        persister: ReportPersister,
    ):
        self._client = client
        self._report_id = report_id
        self._settings = settings
        self._persister = persister

    @property
    def settings(self) -> ReportSettings:
        return self._settings

    def get_report(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
    ) -> ReportAccessorApi:
        url = self._report_id
        response = self._client.post(
            url,
            body={"order": order},
            params=_make_params_dict(
                date=to_maybe_date_string(date),
                date_start=to_maybe_date_string(date_start),
                date_end=to_maybe_date_string(date_end),
                subtotals=subtotals,
            ),
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get report {(response.json())}") from e

        accessor_description = response.json()
        return ReportAccessorClientImpl(
            self._client,
            accessor_description["identifier"],
            ReportAccessorSettings(
                axes=accessor_description["axes"],
                metric_cols=accessor_description["metric_cols"],
                pivot_cols=accessor_description["pivot_cols"],
            ),
            persister=self._persister,
        )

    def dates(self) -> list[dt.date]:
        response = self._client.get(f"{self._report_id}/dates")
        return [to_date(d) for d in response.json()]


class AsyncReportClientImpl(AsyncReportApi):

    def __init__(
        self,
        client: AsyncApiClient,
        report_id: str,
        settings: ReportSettings,
        persister: AsyncReportPersister,
    ):
        self._client = client
        self._report_id = report_id
        self._settings = settings
        self._persister = persister

    @property
    def settings(self) -> ReportSettings:
        return self._settings

    async def get_report(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
    ) -> AsyncReportAccessorApi:
        url = self._report_id
        response = await self._client.post(
            url,
            body={"order": order},
            params=_make_params_dict(
                date=to_maybe_date_string(date),
                date_start=to_maybe_date_string(date_start),
                date_end=to_maybe_date_string(date_end),
                subtotals=subtotals,
            ),
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get report {(response.json())}") from e

        accessor_description = response.json()
        return AsyncReportAccessorClientImpl(
            self._client,
            accessor_description["identifier"],
            ReportAccessorSettings(
                axes=accessor_description["axes"],
                metric_cols=accessor_description["metric_cols"],
                pivot_cols=accessor_description["pivot_cols"],
            ),
            persister=self._persister,
        )

    async def dates(self) -> list[dt.date]:
        response = await self._client.get(f"{self._report_id}/dates")
        return [to_date(d) for d in response.json()]


class ReportLoaderClientImpl(ReportLoaderApi):
    def __init__(
        self,
        client: ApiClient,
        portfoliohierarchy_api: PortfolioHierarchyLoaderApi,
        persister: ReportPersister | None = None,
    ):
        self._client = client.append_base_path("portfolioreport")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/report"),
            ReportSettings,
            ReportSettingsMenu,
        )
        self._accessor_settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-report-accessor"),
            ReportAccessorSettings,
            SettingsMenu[ReportAccessorSettings],
        )
        self._portfoliohierarchy_api = portfoliohierarchy_api
        self._persister = persister or ReportPersisterClient(client)

    @property
    def persister(self) -> ReportPersister:
        return self._persister

    @property
    def settings(
        self,
    ) -> SettingsRegistry[ReportSettings, ReportSettingsMenu]:
        return self._settings

    def load(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
        dates: list[DateLike] | tuple[DateLike, DateLike] | None = None,
    ) -> ReportApi:
        if isinstance(ref_or_settings, ReportSettings):
            settings = ref_or_settings
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(settings)
        else:
            ref = ref_or_settings
            settings = self.settings.get(ref)

        hierarchy: PortfolioHierarchySettings | None = None
        if hierarchy_ref_or_settings is not None:
            if isinstance(hierarchy_ref_or_settings, PortfolioHierarchySettings):
                hierarchy = hierarchy_ref_or_settings
            else:
                hierarchy = (
                    self._portfoliohierarchy_api.load(hierarchy_ref_or_settings)
                ).settings

        dates_params = {"start_date": None, "end_date": None, "dates": None}
        if dates is not None:
            if isinstance(dates, tuple):
                dates_params["start_date"] = to_date_string(dates[0])  # type: ignore
                dates_params["end_date"] = to_date_string(dates[1])  # type: ignore
            else:
                dates_params["dates"] = [to_date_string(d) for d in dates]  # type: ignore

        params = {
            "settings": settings.model_dump(),
            **dates_params,
        }

        params["hierarchy"] = hierarchy.model_dump() if hierarchy else None

        response = self._client.post("", body=params)
        report_id = response.json()["report_id"]
        return ReportClientImpl(
            self._client, report_id, settings, persister=self._persister
        )

    def persisted_report_settings(
        self,
    ) -> ReadOnlyRegistry[ReportAccessorSettings]:
        return self._accessor_settings

    def load_persisted(self, name_or_id: str | int) -> ReportAccessorApi:
        return self._persister.load_persisted(name_or_id)

    def delete_persisted(self, name_or_id: list[str | int]) -> None:
        self._persister.delete_persisted(name_or_id)


class AsyncReportLoaderClientImpl(AsyncReportLoaderApi):
    def __init__(
        self,
        client: AsyncApiClient,
        portfoliohierarchy_api: AsyncPortfolioHierarchyLoaderApi,
        persister: AsyncReportPersister | None = None,
    ):
        self._client = client.append_base_path("portfolioreport")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/report"),
            ReportSettings,
            ReportSettingsMenu,
        )
        self._accessor_settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-report-accessor"),
            ReportAccessorSettings,
            SettingsMenu[ReportAccessorSettings],
        )
        self._portfoliohierarchy_api = portfoliohierarchy_api
        self._persister = persister or AsyncReportPersisterClient(client)

    @property
    def persister(self) -> AsyncReportPersister:
        return self._persister

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[ReportSettings, ReportSettingsMenu]:
        return self._settings

    async def load(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
        dates: list[DateLike] | tuple[DateLike, DateLike] | None = None,
    ) -> AsyncReportApi:
        if isinstance(ref_or_settings, ReportSettings):
            settings = ref_or_settings
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(settings)
        else:
            ref = ref_or_settings
            settings = await self.settings.get(ref)

        hierarchy: PortfolioHierarchySettings | None = None
        if hierarchy_ref_or_settings is not None:
            if isinstance(hierarchy_ref_or_settings, PortfolioHierarchySettings):
                hierarchy = hierarchy_ref_or_settings
            else:
                hierarchy = (
                    await self._portfoliohierarchy_api.load(hierarchy_ref_or_settings)
                ).settings

        dates_params = {"start_date": None, "end_date": None, "dates": None}
        if dates is not None:
            if isinstance(dates, tuple):
                dates_params["start_date"] = to_date_string(dates[0])  # type: ignore
                dates_params["end_date"] = to_date_string(dates[1])  # type: ignore
            else:
                dates_params["dates"] = [to_date_string(d) for d in dates]  # type: ignore

        params = {
            "settings": settings.model_dump(),
            **dates_params,
        }

        params["hierarchy"] = hierarchy.model_dump() if hierarchy else None

        response = await self._client.post("", body=params)
        report_id = response.json()["report_id"]
        return AsyncReportClientImpl(
            self._client, report_id, settings, persister=self._persister
        )

    @property
    def persisted_report_settings(
        self,
    ) -> AsyncReadOnlyRegistry[ReportAccessorSettings]:
        return self._accessor_settings

    async def load_persisted(self, name_or_id: str | int) -> AsyncReportAccessorApi:
        return await self._persister.load_persisted(name_or_id)

    async def delete_persisted(self, name_or_id: list[str | int]) -> None:
        await self._persister.delete_persisted(name_or_id)


class AsyncReportPersisterClient(AsyncReportPersister):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("portfolioreport")
        self._settings_client = client.append_base_path(
            "settings/portfolio-report-accessor"
        )

    async def persist(
        self,
        name: str,
        settings: ReportAccessorSettings,
        accessors: list[AsyncReportAccessorApi],
    ) -> int:
        body = {
            "settings": settings.model_dump(),
            "accessor_identifiers": [a.identifier for a in accessors],
        }
        response = await self._client.post(f"accessor/{name}", body=body)
        response.raise_for_status()
        return response.json()["id"]

    async def load_persisted(self, name_or_id: str | int) -> AsyncReportAccessorApi:
        accessor_settings = AsyncHttpSettingsRegistryClient(
            self._settings_client,
            ReportAccessorSettings,
            SettingsMenu[ReportAccessorSettings],
        )
        settings = await accessor_settings.get(name_or_id)

        identifier: int
        if isinstance(name_or_id, str):
            identifier = (await accessor_settings.names())[name_or_id]
        else:
            identifier = name_or_id

        return AsyncReportAccessorClientImpl(
            self._client, identifier, settings, persister=self
        )

    async def delete_persisted(self, name_or_id: list[str | int]) -> None:
        names: list[str] = []
        ids: list[int] = []
        for e in name_or_id:
            if isinstance(e, int):
                ids.append(e)
            else:
                names.append(e)
        params = {"name": names, "id": ids}
        result = await self._client.delete("accessor", params=params)
        result.raise_for_status()


class ReportPersisterClient(ReportPersister):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("portfolioreport")
        self._settings_client = client.append_base_path(
            "settings/portfolio-report-accessor"
        )

    def persist(
        self,
        name: str,
        settings: ReportAccessorSettings,
        accessors: list[ReportAccessorApi],
    ) -> int:
        body = {
            "settings": settings.model_dump(),
            "accessor_identifiers": [a.identifier for a in accessors],
        }
        response = self._client.post(f"accessor/{name}", body=body)
        response.raise_for_status()
        return response.json()["id"]

    def load_persisted(self, name_or_id: str | int) -> AsyncReportAccessorApi:
        accessor_settings = HttpSettingsRegistryClient(
            self._settings_client,
            ReportAccessorSettings,
            SettingsMenu[ReportAccessorSettings],
        )
        settings = accessor_settings.get(name_or_id)
        identifier: int
        if isinstance(name_or_id, str):
            identifier = (accessor_settings.names())[name_or_id]
        else:
            identifier = name_or_id

        return ReportAccessorClientImpl(
            self._client, identifier, settings, persister=self
        )

    def delete_persisted(self, name_or_id: list[str | int]) -> None:
        names: list[str] = []
        ids: list[int] = []
        for e in name_or_id:
            if isinstance(e, int):
                ids.append(e)
            else:
                names.append(e)
        params = {"names": names, "ids": ids}
        result = self._client.delete("accessor", params=params)
        result.raise_for_status()
