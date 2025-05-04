from __future__ import annotations
from crypticorn.klines import (
    ApiClient,
    Configuration,
    FundingRatesApi,
    StatusApi,
    OHLCVDataApi,
    SymbolsApi,
    UDFApi,
)
from crypticorn.common import optional_import


class KlinesClient:
    """
    A client for interacting with the Crypticorn Klines API.
    """

    config_class = Configuration

    def __init__(
        self,
        config: Configuration,
    ):
        self.config = config
        self.base_client = ApiClient(configuration=self.config)
        # Instantiate all the endpoint clients
        self.funding = FundingRatesApiWrapper(self.base_client)
        self.ohlcv = OHLCVDataApiWrapper(self.base_client)
        self.symbols = SymbolsApiWrapper(self.base_client)
        self.udf = UDFApi(self.base_client)
        self.status = StatusApi(self.base_client)


class FundingRatesApiWrapper(FundingRatesApi):
    """
    A wrapper for the FundingRatesApi class.
    """

    async def get_funding_rates_fmt(self, *args, **kwargs) -> pd.DataFrame:  # type: ignore
        """
        Get the funding rates in a pandas DataFrame.
        """
        pd = optional_import("pandas", "extra")
        response = await self.get_funding_rates(*args, **kwargs)
        response = [
            {
                "timestamp": int(m.timestamp.timestamp()),
                "symbol": m.symbol,
                "funding_rate": m.funding_rate,
            }
            for m in response
        ]
        return pd.DataFrame(response)


class OHLCVDataApiWrapper(OHLCVDataApi):
    """
    A wrapper for the OHLCVDataApi class.
    """

    async def get_ohlcv_data_fmt(self, *args, **kwargs) -> pd.DataFrame:  # type: ignore
        """
        Get the OHLCV data in a pandas DataFrame.
        """
        pd = optional_import("pandas", "extra")
        response = await self.get_ohlcv(*args, **kwargs)
        df = pd.DataFrame(
            {
                "timestamp": [int(d.timestamp()) for d in response.timestamps],
                "open": response.open,
                "high": response.high,
                "low": response.low,
                "close": response.close,
                "volume": response.volume,
            }
        )
        df.sort_values(by="timestamp", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df


class SymbolsApiWrapper(SymbolsApi):
    """
    A wrapper for the SymbolsApi class.
    """

    async def get_symbols_fmt(self, *args, **kwargs) -> pd.DataFrame:  # type: ignore
        """
        Get the symbols in a pandas DataFrame.
        """
        pd = optional_import("pandas", "extra")
        response = await self.get_klines_symbols(*args, **kwargs)
        return pd.DataFrame(response, columns=["symbol"])
