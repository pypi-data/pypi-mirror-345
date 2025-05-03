from __future__ import annotations
from crypticorn.metrics import (
    ApiClient,
    Configuration,
    ExchangesApi,
    StatusApi,
    IndicatorsApi,
    LogsApi,
    MarketcapApi,
    MarketsApi,
    TokensApi,
)
from crypticorn.common import optional_import


class MetricsClient:
    """
    A client for interacting with the Crypticorn Metrics API.
    """

    config_class = Configuration

    def __init__(
        self,
        config: Configuration,
    ):
        self.config = config
        self.base_client = ApiClient(configuration=self.config)
        # Instantiate all the endpoint clients
        self.status = StatusApi(self.base_client)
        self.indicators = IndicatorsApi(self.base_client)
        self.logs = LogsApi(self.base_client)
        self.marketcap = MarketcapApiWrapper(self.base_client)
        self.markets = MarketsApi(self.base_client)
        self.tokens = TokensApiWrapper(self.base_client)
        self.exchanges = ExchangesApiWrapper(self.base_client)


class MarketcapApiWrapper(MarketcapApi):
    """
    A wrapper for the MarketcapApi class.
    """

    async def get_marketcap_symbols_fmt(self, *args, **kwargs) -> pd.DataFrame:  # type: ignore
        """
        Get the marketcap symbols in a pandas dataframe
        """
        pd = optional_import("pandas", "extra")
        response = await self.get_marketcap_symbols(*args, **kwargs)
        df = pd.DataFrame(response)
        df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)
        return df


class TokensApiWrapper(TokensApi):
    """
    A wrapper for the TokensApi class.
    """

    async def get_stable_and_wrapped_tokens_fmt(self, *args, **kwargs) -> pd.DataFrame:  # type: ignore
        """
        Get the tokens in a pandas dataframe
        """
        pd = optional_import("pandas", "extra")
        response = await self.get_stable_and_wrapped_tokens(*args, **kwargs)
        return pd.DataFrame(response)


class ExchangesApiWrapper(ExchangesApi):
    """
    A wrapper for the ExchangesApi class.
    """

    async def get_available_exchanges_fmt(self, *args, **kwargs) -> pd.DataFrame:  # type: ignore
        """
        Get the exchanges in a pandas dataframe
        """
        pd = optional_import("pandas", "extra")
        response = await self.get_available_exchanges(*args, **kwargs)
        processed_results = []
        for row in response:
            data = {"timestamp": row["timestamp"]}
            data.update(row["exchanges"])
            processed_results.append(data)

        # Create DataFrame and sort columns
        df = pd.DataFrame(processed_results)
        cols = ["timestamp"] + sorted([col for col in df.columns if col != "timestamp"])
        df = df[cols]

        # Convert timestamp to unix timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"]).astype("int64") // 10**9

        # Convert exchange availability to boolean integers (0/1)
        df = df.astype(
            {
                "timestamp": "int64",
                **{col: "int8" for col in df.columns if col != "timestamp"},
            }
        )
        return df
