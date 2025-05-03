# py-bls-api
# Author: Christopher Morris
# License: Non-Commercial, No-Derivatives License
#
# You may use this code for personal, educational, or non-commercial research purposes
# with proper attribution. Commercial use, redistribution, or modification is not allowed
# without explicit permission from the author.
#
# For full license terms, see the LICENSE file.

import pandas as pd
import requests
from typing import Any, List, Dict, Tuple, Optional, Union
    
def get_surveys() -> Dict[str, str]:
    """
    Returns a dictionary of BLS surveys supported by py-bls-api.
    """
    url = r"https://coding-with-chris.github.io/py-bls-api/metadata/bls-datasets.json"
    response = requests.get(url)

    return response.json()


def get_survey_metadata(survey_abbreviation: str) -> Dict[str, Any]:
    """
    Returns a dictionary containing metadata for a given survey (e.g., 'IP', 'CU').
    """
    url = fr"https://coding-with-chris.github.io/py-bls-api/metadata/{survey_abbreviation.upper()}.json"
    response = requests.get(url)

    return response.json()


def get_data_preview(survey_abbreviation: str) -> pd.DataFrame:
    """
    Returns a dataframe containing a data preview for a given survey (e.g., 'IP', 'CU').
    """
    data_preview = get_survey_metadata(survey_abbreviation)['data_preview']

    return pd.DataFrame(data_preview)


def get_seriesid_metadata(survey_abbreviation: str) -> pd.DataFrame:
    """
    Returns a dataframe containing Series ID metadata for a given survey (e.g., 'IP', 'CU').
    """
    seriesid_metadata = get_survey_metadata(survey_abbreviation)['series']
    
    return pd.DataFrame(seriesid_metadata)


def get_popular_seriesids(survey_abbreviation: str, registrationkey: str) -> List[str]:
    """
    Returns a list of popular BLS Series IDs for a given survey (e.g., 'CU', 'CE').

    Parameters:
    - survey_abbreviation: Survey code to filter popular series (e.g., 'CU').
    - registrationkey: The BLS API registration key. Register at https://data.bls.gov/registrationEngine/.

    Returns:
    - A list of popular Series IDs. Returns an empty list if none are found or if the request fails.
    """    
    # request URL
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/popular?survey={survey_abbreviation.upper()}"
    params = {"registrationkey": registrationkey}

    # fetch popular Series IDs
    response = requests.get(url, params=params)

    # process API response and extract Series IDs
    if response.status_code == 200:
        popular_series = response.json().get("Results", {}).get("series", [])
        return [item.get("seriesID") for item in popular_series if item]
    else:
        return []


def validate_parameters(seriesids: List[str], startyear: int, endyear: int, registrationkey: str, metadata: Dict[str, Any]) -> None:
    """
    Validates parameters for get_bls_data.

    Parameters:
    -seriesids: List of Series IDs.
    -startyear: Start year for data request.
    -endyear: End year for data request.
    -registrationkey: BLS API key.
    -metadata: Survey metadata dictionary.

    Raises:
        TypeError, ValueError: If parameters are invalid.
    """

    # validate that Series IDs are passed in as a list and that at least 1 is provided
    if not isinstance(seriesids, list):
        raise TypeError("The seriesids parameter must be a list.")   
    if not seriesids:
        raise ValueError("You must provide at least one Series ID.")

    # validate that all Series IDs are from the same survey        
    survey_abbreviation = seriesids[0][:2].upper()    
    if len(seriesids) > 1:    
        if not all(seriesid.startswith(survey_abbreviation) for seriesid in seriesids):
            raise ValueError("All Series IDs must be from the same survey.")

    # validate that Series IDs are from a survey supported by py-bls-api                    
    supported_surveys = get_surveys()
    survey_abbreviations = [abbr.upper() for abbr in supported_surveys.values()]                
    if survey_abbreviation not in survey_abbreviations:
        raise ValueError(f"Survey abbreviation '{survey_abbreviation}' is not currently supported by the py-bls-api wrapper.")

    # validate that Series IDs are found in the metadata.        
    valid_series_ids = {valid_series["id"] for valid_series in metadata["series"]}
    invalid_seriesids = [series for series in seriesids if series not in valid_series_ids]
    if invalid_seriesids:
        raise ValueError(f"Invalid Series ID(s) found: {', '.join(invalid_seriesids)}. Check the survey metadata for more information.")

    # validate start and end years.
    if not isinstance(startyear, int):
        raise TypeError("The startyear must be an integer.")
    if not isinstance(endyear, int):
        raise TypeError("The endyear must be an integer.")        
    if startyear and not endyear:
        raise ValueError("If the startyear is provided, the endyear must also be provided.")
    if not startyear and endyear:
        raise ValueError("If the endyear is provided, the startyear must also be provided.")
    if startyear > endyear:
        raise ValueError("The startyear cannot be greater than the endyear.")  
        
    # validate that the users passes an API key.
    if not registrationkey:
        raise ValueError("You must provide a valid BLS API key.")
        

def group_series_for_user_range(seriesids: List[str], series_lookup: Dict[str, Tuple[int, int]], user_startyear: int, user_endyear: int, log_messages: List[str]) -> Dict[Tuple[int, int], List[str]]:
    """
    Groups series IDs by the overlapping range based on the user's request.
    Returns a dictionary where keys are (startyear, endyear) tuples and values are lists of Series IDs.
    """
    grouped = {}

    for series in seriesids:
        metadata_startyear, metadata_endyear = series_lookup[series]

        # calculate the overlapping range
        effective_startyear = max(metadata_startyear, user_startyear)
        effective_endyear = min(metadata_endyear, user_endyear)

        if effective_startyear > effective_endyear:
            log_messages.append(f"Series ID {series} has no overlap with requested range {user_startyear}-{user_endyear}. Skipping.")
            continue

        key = (effective_startyear, effective_endyear)
        grouped.setdefault(key, []).append(series)

    return grouped

def split_series_chunks(series_list: List[str], chunk_size: int = 50) -> List[List[str]]:
    """
    Splits a list of Series IDs into chunks of 50 to comply with BLS API limits.
    """
    return [series_list[i:i + chunk_size] for i in range(0, len(series_list), chunk_size)]

def split_year_chunks(startyear: int, endyear: int, chunk_size: int = 20) -> List[Tuple[int, int]]:
    """
    Splits a range of years into chunks of 20 years to comply with BLS API limits.
    """
    return [(i, min(i + chunk_size - 1, endyear)) for i in range(startyear, endyear + 1, chunk_size)]

def fetch_bls_data(payload: Dict[str, Any], request_url: str, log_messages: List[str]) -> Optional[Dict[str, Any]]:
    """
    Requests data from the BLS API and returns the JSON response if successful.

    Parameters:
    -payload: Dictionary containing API request parameters (e.g., seriesid, startyear).
    -request_url: URL of the BLS API endpoint.
    -log_messages: List to append error messages if the request fails.

    Returns:
        Dictionary containing the API response, or None if the request fails.
    """
    response = requests.post(request_url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        log_messages.append(f"Failed to fetch data. HTTP {response.status_code} — Payload: {payload}")
        return None

def process_api_response(data: Dict[str, Any], year_start: int, year_end: int, log_messages: List[str]) -> List[Dict[str, Any]]:
    """
    Processes API response and extracts records, logging messages and missing data.

    Parameters:
    -data: Dictionary containing the BLS API response.
    -year_start: Start year of the requested data range.
    -year_end: End year of the requested data range.
    -log_messages: List to append messages for API issues or missing data.

    Returns:
        List of dictionaries, each representing a data record with catalog metadata.
    """
    collect = []
    if data.get("message"):
        for message in data["message"]:
            api_message = f"{message}"
            if api_message not in log_messages:
                log_messages.append(api_message)

    if "Results" in data and "series" in data["Results"]:
        for series in data["Results"]["series"]:
            series_id = series.get("seriesID", "unknown_seriesID")
            catalog_metadata = series.get("catalog", {})
            
            if not series.get("data"):
                log_messages.append(f"No data for {series_id} in {year_start}-{year_end}")
                continue
            
            for record in series["data"]:
                record.update(catalog_metadata)
                collect.append(record)
                
    return collect

def get_bls_data(seriesids: List[str], startyear: int, endyear: int, registrationkey: str, catalog: bool = True, calculations: bool = False, annualaverage: bool = False, aspects: bool = False, return_logs: bool = True) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
    """
    Fetches data and metadata from the BLS API for a list of Series IDs within a specified year range.
    
    Parameters:
    - seriesids: List of Series IDs to fetch data for.
    - startyear: The start year for the data request.
    - endyear: The end year for the data request.
    - registrationkey: The BLS API registration key. Register at https://data.bls.gov/registrationEngine/.
    - catalog, calculations, annualaverage, aspects: Optional flags to include additional data in the response.
    - return_logs: If True, returns a tuple of data and log DataFrames; if False, returns only the data DataFrame.

    Returns:
    - Requested data as a dataframe or a tuple of dataframes containing data and log messages.
    """    
    log_messages = []

    # load survey metadata
    survey_abbreviation = seriesids[0][:2].upper()
    metadata = get_survey_metadata(survey_abbreviation)

    # validate function parameters
    try:
        validate_parameters(seriesids, startyear, endyear, registrationkey, metadata)
    except Exception as e:
        log_messages.append(str(e))
        return pd.DataFrame(), pd.DataFrame({"log": log_messages})

    # create Series ID lookup of valid year ranges from survey metadata        
    series_lookup = {series["id"]: series["year_range"] for series in metadata["series"]}

    # Group Series IDs by effective year range based on overlap of metadata and user input. 
    grouped_series = group_series_for_user_range(seriesids, series_lookup, startyear, endyear, log_messages)

    # base url to BLS API
    request_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    collect_all = []    
   
    for (group_startyear, group_endyear), grouped_ids in grouped_series.items():
        year_chunks = [(group_startyear, group_endyear)] if (group_endyear - group_startyear + 1) <= 20 else split_year_chunks(group_startyear, group_endyear)
        collect_dfs = []
        
        for year_start, year_end in year_chunks:
            for chunk in split_series_chunks(grouped_ids):
        
                payload = {
                    "seriesid":chunk,
                    "catalog":catalog,
                    "calculations":calculations,
                    "annualaverage":annualaverage,
                    "aspects":aspects,                
                    "registrationkey":registrationkey,
                    "startyear": str(year_start),
                    "endyear": str(year_end)
                }
                
                data = fetch_bls_data(payload, request_url, log_messages)
                
                if data:
                    records = process_api_response(data, year_start, year_end, log_messages)
                    df = pd.DataFrame(records)
            
                    # move the catalog information to the left hand side of the dataframe
                    if not df.empty:
                        reorder_columns = ['survey_name','survey_abbreviation','series_id','series_title']
                        df = df[reorder_columns + [col for col in df.columns if col not in reorder_columns]]        
                        collect_dfs.append(df)
            
        if collect_dfs:
            dataset = pd.concat(collect_dfs)
            collect_all.append(dataset)
    
    if collect_all:
        dataset_all = pd.concat(collect_all)  
        
    else:
        log_messages.append("No data was returned for the specified Series IDs and date range.")        
        dataset_all = pd.DataFrame(columns=['survey_name', 'survey_abbreviation', 'series_id', 'series_title', 'year', 'period', 'value'])

    if return_logs:
        return dataset_all, pd.DataFrame({"log": log_messages})
    
    return dataset_all
