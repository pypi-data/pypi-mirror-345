import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("JQuants-MCP-server")

async def make_requests(url: str,timeout: int = 30) -> dict[str, Any]:
    """
    Function to process requests

    Args:
        url (str): URL for the request
        timeout (int, optional): Timeout in seconds. Default is 30 seconds.

    Returns:
        str: API response text
    """
    try:
        idToken = os.environ.get("JQUANTS_ID_TOKEN", "")
        if not idToken:
            return {"error": "JQUANTS_ID_TOKENが設定されていません。", "status": "id_token_error"}

        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {'Authorization': 'Bearer {}'.format(idToken)}
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return {"error": f"APIリクエストに失敗しました。ステータスコード: {response.status_code}", "status": "request_error"}
            if response.headers.get("Content-Type") != "application/json":
                return {"error": "APIレスポンスがJSON形式ではありません。", "status": "response_format_error"}

            return json.loads(response.text)

    except Exception as e:
        if isinstance(e, httpx.TimeoutException):
            error_msg =  f"タイムアウトエラーが発生しました。現在のタイムアウト設定: {timeout}秒"
            return {"error": error_msg, "status": "timeout"}
        elif isinstance(e, httpx.ConnectError):
            error_msg = "E-Stat APIサーバーへの接続に失敗しました。ネットワーク接続を確認してください。"
            return {"error": error_msg, "status": "connection_error"}
        elif isinstance(e, httpx.HTTPStatusError):
            error_msg = f"HTTPエラー（ステータスコード: {e.response.status_code}）が発生しました。"
            return {"error": error_msg, "status": "http_error"}
        else:
            error_msg = f"予期せぬエラーが発生しました: {str(e)}"
            return {"error": error_msg, "status": "unexpected_error"}


@mcp_server.tool()
async def search_company(
        query : str,
        limit : int = 10,
        start_position : int = 0,
    ) -> str:
    """
    Search for listed stocks by company name.

    Args:
        query (str): Query parameter for searching company names. Specify a string contained in the company name.
            Example: Specifying "トヨタ" will search for stocks with "トヨタ" in the company name.
            Must be in Japanese.
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text
    """
    url = "https://api.jquants.com/v1/listed/info"
    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)

    response_json_list = response.get("info", [])
    response_json_list = [
        r for r in response_json_list
        if (
            query.lower() in r.get("CompanyName", "").lower()
            or
            query.lower() in r.get("CompanyNameEnglish", "").lower()
        )
    ][start_position:start_position + limit]

    response_json = {'info': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)



@mcp_server.tool()
async def get_daily_quotes(
        code : str,
        from_date : str,
        to_date : str,
        limit : int = 10,
        start_position : int = 0,
    ) -> str:
    """
    Retrieve daily stock price data for a specified stock code.
    The available data spans from 2 years prior to today up until 12 weeks ago.

    Args:
        code (str): Specify the stock code. Example: "72030" (トヨタ自動車)
        from_date (str): Specify the start date. Example: "2023-01-01" must be in YYYY-MM-DD format
        to_date (str): Specify the end date. Example: "2023-01-31" must be in YYYY-MM-DD format
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text
    """

    url = "https://api.jquants.com/v1/prices/daily_quotes?code={}&from={}&to={}".format(
        code,
        from_date,
        to_date
    )
    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)
    response_json_list = response.get("daily_quotes", [])
    response_json_list = response_json_list[start_position:start_position + limit]
    response_json = {'daily_quotes': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)


@mcp_server.tool()
async def get_financial_statements(
        code : str,
        limit : int = 10,
        start_position : int = 0,
    ) -> str:
    """
    Retrieve financial statements for a specified stock code.
    The available data spans from 2 years prior to today up until 12 weeks ago.
    You can obtain quarterly financial summary reports and disclosure information regarding
    revisions to performance and dividend information (mainly numerical data) for listed companies.

    Args:
        code (str): Specify the stock code. Example: "72030" (トヨタ自動車)
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.
    """
    url = "https://api.jquants.com/v1/fins/statements?code={}".format(code)
    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)
    response_json_list = response.get("statements", [])
    response_json_list = [
        {k:v for k,v in r.items() if v != ""}
        for r in response_json_list
    ][start_position:start_position + limit]
    response_json = {'statements': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)


def main() -> None:
    print("Starting J-Quants MCP server!")
    mcp_server.run(transport="stdio")

if __name__ == "__main__":
    main()