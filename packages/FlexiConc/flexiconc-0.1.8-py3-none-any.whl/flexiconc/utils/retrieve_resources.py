import requests
import pandas as pd
from flexiconc.resources import ResourceRegistry


def register_sketchengine_freq_list(
    self,
    resource_name: str,
    corpname: str,
    wlattr: str = 'lc',
    wlstruct_attr: str = 'word',
    wlnums: str = 'frq',
    wlminfreq: int = 1,
    wlmaxitems: int = 1000000000,
    wlpat: str = '.*',
    wlicase: int = 0,
    wltype: str = 'simple',
    details: dict = None,
    api_username: str = 'anonymous',
    api_key: str = '66260be9038677cd68a2559ec1153f20',
):
    """
    Fetches a frequency list from the SketchEngine Struct Wordlist API
    and registers it as a 'frequency_list' resource in the provided Concordance.

    Parameters:
    - concordance: Concordance instance with a ResourceRegistry at .resources
    - resource_name: name to register the frequency list under
    - corpname: SketchEngine corpus name (e.g. 'preloaded/bnc2_tt21')
    - wlattr: wordlist attribute for frequency (default 'lc')
    - wlstruct_attr: struct attribute name for tokens (default 'word')
    - wlnums: numeric field to fetch (default 'frq')
    - wlminfreq: minimum frequency (default 1),
    - wlmaxitems: maximum number of items to fetch (default 1e9)
    - wlpat: regex pattern to match (default '.*')
    - wlicase: case sensitivity (0 or 1)
    - wltype: type of wordlist (default 'simple')
    - details: optional metadata dict
    """
    # Build API URL and parameters
    url = 'https://api.sketchengine.eu/search/struct_wordlist'
    auth = (api_username, api_key)
    params = {
        'corpname': corpname,
        'wlattr': wlattr,
        'wlstruct_attr1': wlstruct_attr,
        'wlnums': wlnums,
        'wlminfreq': wlminfreq,
        'wlmaxitems': wlmaxitems,
        'wlpat': wlpat,
        'wlicase': wlicase,
        'wltype': wltype
    }

    # Make GET request
    response = requests.get(url, params=params, auth=auth)
    response.raise_for_status()
    data = response.json()

    # Extract items
    blocks = data.get('Blocks', [])
    if not blocks:
        raise ValueError('No Blocks returned from SketchEngine API')

    items = blocks[0].get('Items', [])
    if not items:
        raise ValueError('No Items in Blocks[0]')

    # Build DataFrame
    records = []
    for item in items:
        # token value under wlstruct_attr1, JSON key capitalized
        token_list = item.get('Word', [])
        if not token_list:
            continue
        token = token_list[0].get('n')
        freq = item.get(wlnums)
        records.append({wlstruct_attr: token, 'f': freq})

    df = pd.DataFrame.from_records(records, columns=[wlstruct_attr, 'f'])

    # Register in registry
    conc_resources: ResourceRegistry = self.resources
    conc_resources.register(
        name=resource_name,
        resource=df,
        resource_type='frequency_list',
        details={**(details or {}), 'source': 'sketchengine', 'corpname': corpname, 'token_attr': wlstruct_attr}
    )

    return None
