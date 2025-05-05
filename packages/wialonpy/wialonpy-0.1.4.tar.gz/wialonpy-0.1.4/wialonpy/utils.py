import json
import logging
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_WIALON_URL = "https://hst-api.wialon.com/wialon/ajax.html"


class WialonAuthError(Exception):
    """Raised when Wialon authentication fails."""
    pass


class WialonAPIError(Exception):
    """Raised when Wialon API returns invalid or unexpected data."""
    pass


def get_session_eid(w_token: str, wialon_url: str = DEFAULT_WIALON_URL) -> Optional[str]:
    """
    Authenticate with Wialon API using a token and return the session ID (eid).

    Args:
        w_token (str): Wialon API token.
        wialon_url (str): URL to Wialon API. Defaults to production endpoint.

    Returns:
        Optional[str]: Session ID (eid) if successful, otherwise None.

    Raises:
        WialonAuthError: If the authentication fails.
        requests.exceptions.RequestException: If the request fails.
    """
    try:
        params = {
            "svc": "token/login",
            "params": json.dumps({"token": w_token}),
        }
        response = requests.post(wialon_url, params=params)
        response.raise_for_status()

        data = response.json()
        eid = data.get("eid")

        if not eid:
            logger.warning("Wialon returned no session ID: %s", data)
            raise WialonAuthError("No session ID returned by Wialon")

        return eid

    except requests.RequestException as e:
        logger.error("Wialon request failed: %s", e)
        raise
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Wialon response: %s", e)
        raise WialonAuthError("Invalid JSON response from Wialon")


def get_wialon_object_id(group_name: str, eid: str, wialon_url: str = DEFAULT_WIALON_URL) -> str:
    """
    Retrieve the ID of a unit group by its name from Wialon.

    Args:
        group_name (str): Name of the unit group to search.
        eid (str): Session ID obtained from Wialon.
        wialon_url (str): Base URL to the Wialon API.

    Returns:
        str: ID of the unit group with the given name.

    Raises:
        requests.exceptions.RequestException: Network-related error.
        WialonAPIError: If the group is not found or response structure is unexpected.
    """
    try:
        params = {
            "svc": "core/search_items",
            "params": json.dumps({
                "spec": {
                    "itemsType": "avl_unit_group",
                    "propName": "sys_name",
                    "propValueMask": "*",
                    "sortType": "sys_id"
                },
                "force": 1,
                "flags": 1,
                "from": 0,
                "to": 0
            }),
            "sid": eid
        }
        response = requests.get(wialon_url, params=params)
        response.raise_for_status()

        data = response.json()
        items = data.get("items")
        if not items or not isinstance(items, list):
            logger.error("Unexpected Wialon response format: %s", data)
            raise WialonAPIError("No unit groups returned from Wialon")

        for item in items:
            if item.get("nm") == group_name:
                return str(item["id"])

        # Если не найдено — собрать список всех групп для вывода
        group_list = [f"{item.get('nm')} (id={item.get('id')})" for item in items]
        message = (
            f"Group '{group_name}' not found. Available groups: "
            + ", ".join(group_list)
        )
        logger.error(message)
        raise WialonAPIError(message)

    except requests.RequestException as e:
        logger.error("Wialon API request failed: %s", e)
        raise
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Failed to parse Wialon response: %s", e)
        raise WialonAPIError("Invalid response format from Wialon") from e


def get_wialon_report_id(report_name: str, sid: str, wialon_url: str = DEFAULT_WIALON_URL) -> tuple[str, str]:
    """
    Retrieve the ID of a report template by name along with its resource ID.

    Args:
        sid (str): Session ID for Wialon.
        report_name (str): The name of the report template to find.
        wialon_url (str): Base URL to the Wialon API.

    Returns:
        tuple[str, str]: Tuple of (template_id, resource_id).

    Raises:
        requests.exceptions.RequestException: If the request fails.
        WialonAPIError: If the report is not found or response is invalid.
    """
    try:
        params = {
            "svc": "core/search_items",
            "params": json.dumps({
                "spec": {
                    "itemsType": "avl_resource",
                    "propName": "reporttemplates",
                    "propValueMask": "*",
                    "sortType": "sys_id"
                },
                "force": 1,
                "flags": "4611686018427387903",
                "from": 0,
                "to": 0
            }),
            "sid": sid
        }
        response = requests.get(wialon_url, params=params)
        response.raise_for_status()
        data = response.json()

        for report in data.get("items", []):
            templates = report.get("rep", {}).values()
            for template in templates:
                if template.get("n") == report_name:
                    return str(template["id"]), str(report["id"])

        report_list = [f"{tpl.get('n')} (template_id={tpl.get('id')}, resource_id={report.get('id')})"
                       for report in data.get("items", [])
                       for tpl in report.get("rep", {}).values()]
        message = f"Report '{report_name}' not found. Available templates: " + ", ".join(report_list)
        logger.error(message)
        raise WialonAPIError(message)

    except requests.RequestException as e:
        logger.error("Wialon API request failed: %s", e)
        raise
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Failed to parse Wialon response: %s", e)
        raise WialonAPIError("Invalid response format from Wialon") from e


def wialon_exec_report(sid: str, time_from: int, time_to: int, object_id: str, resource_id: str, template_id: str,
                       wialon_url: str = DEFAULT_WIALON_URL) -> dict:
    """
    Execute a Wialon report and return the raw response data.

    Args:
        sid (str): Wialon session ID.
        time_from (int): Start of the interval (Unix time).
        time_to (int): End of the interval (Unix time).
        object_id (str): ID of the Wialon object.
        resource_id (str): ID of the report's resource.
        template_id (str): ID of the report template.
        wialon_url (str): Wialon API URL.

    Returns:
        dict: Parsed JSON response from the Wialon API.

    Raises:
        requests.exceptions.RequestException: If the request fails.
        WialonAPIError: If the response is invalid.
    """
    try:
        params = {
            "svc": "report/exec_report",
            "params": json.dumps({
                "reportResourceId": int(resource_id),
                "reportTemplateId": int(template_id),
                "reportObjectId": int(object_id),
                "reportObjectSecId": 0,
                "interval": {
                    "from": int(time_from),
                    "to": int(time_to),
                    "flags": 0
                }
            }),
            "sid": sid
        }
        response = requests.get(wialon_url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.debug("Wialon exec_report response: %s", data)
        return data

    except requests.RequestException as e:
        logger.error("Wialon report execution failed: %s", e)
        raise
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        logger.error("Invalid response from Wialon exec_report: %s", e)
        raise WialonAPIError("Failed to execute report or parse response") from e


def wialon_select_result(
    sid: str,
    table_indices: List[int] = [0],
    row_from: int = 0,
    row_to: int = 62,
    level: int = 2,
    wialon_url: str = DEFAULT_WIALON_URL
) -> dict:
    """
    Select and retrieve rows from the Wialon report result.

    Args:
        sid (str): Wialon session ID.
        table_indices (List[int]): Indices of report tables to fetch.
        row_from (int): Starting row index (default: 0).
        row_to (int): Ending row index (default: 62).
        level (int): Nesting level for rows (default: 2).
        wialon_url (str): Wialon API endpoint URL.

    Returns:
        dict: Parsed JSON response from the batch select_result_rows call.

    Raises:
        requests.exceptions.RequestException: For network issues.
        WialonAPIError: For invalid API responses.
    """
    try:
        if row_from < 0:
            raise ValueError(f"'row_from' must be >= 0 (got {row_from})")
        if row_to < row_from:
            raise ValueError(f"'row_to' must be >= 'row_from' (got {row_to} < {row_from})")
        if level not in (0, 1, 2):
            raise ValueError(f"'level' must be 0, 1 or 2 (got {level})")

        batch_params = [
            {
                "svc": "report/select_result_rows",
                "params": {
                    "tableIndex": table_index,
                    "config": {
                        "type": "range",
                        "data": {
                            "from": row_from,
                            "to": row_to,
                            "level": level
                        },
                    },
                },
            }
            for table_index in table_indices
        ]

        params = {
            "svc": "core/batch",
            "params": json.dumps(batch_params),
            "sid": sid
        }

        response = requests.get(wialon_url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.debug("Wialon select_result response: %s", data)
        return data

    except requests.RequestException as e:
        logger.error("Wialon select_result request failed: %s", e)
        raise
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        logger.error("Invalid response from Wialon select_result: %s", e)
        raise WialonAPIError("Failed to select report result rows") from e


def get_wialon_units(sid: str, wialon_url: str = DEFAULT_WIALON_URL, flags: int = 9) -> List[Dict[str, str]]:
    """
    Retrieve the list of units (avl_unit) from Wialon.

    Args:
        sid (str): Wialon session ID.
        wialon_url (str): Wialon API URL.
        flags (int): Bitmask to define which fields to return for each unit. Default is 9 (id + name).

    Returns:
        List[Dict[str, str]]: List of units with 'id' and 'name'.

    Raises:
        requests.exceptions.RequestException: If the request fails.
        WialonAPIError: If the response is invalid or empty.
    """
    try:
        params = {
            "svc": "core/search_items",
            "params": json.dumps({
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "avl_unit",
                    "propValueMask": "*",
                    "sortType": "sys_id"
                },
                "force": 1,
                "flags": flags,
                "from": 0,
                "to": 0
            }),
            "sid": sid
        }

        response = requests.get(wialon_url, params=params)
        logger.debug("Wialon get_units request URL: %s", response.url)
        response.raise_for_status()
        data = response.json()

        raw_units = data.get("items", [])
        if not isinstance(raw_units, list):
            raise WialonAPIError("Invalid format: 'items' is not a list")

        units = [{"id": str(unit.get("id")), "name": unit.get("nm", "")} for unit in raw_units]
        logger.info("Retrieved %d units from Wialon.", len(units))
        return units

    except requests.RequestException as e:
        logger.error("Wialon API request failed: %s", e)
        raise
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        logger.error("Failed to parse Wialon response: %s", e)
        raise WialonAPIError("Invalid response format from Wialon") from e
