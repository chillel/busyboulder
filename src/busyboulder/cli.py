import re
import ast
import yaml
import click
import requests
from typing import List
try:
    import importlib.resources as pkg_resources
except:
    # Try backported version
    import importlib_resources as pkg_resources

from bs4 import BeautifulSoup

DEFAULT_GYM = "sbp"
NON_BREAK_SPACE = "&nbsp" # to clean up HTML
CONFIG_FILE = pkg_resources.read_text("busyboulder.data", "gym_data.yaml")
BASE_URL="https://portal.rockgympro.com/portal/public"

def build_url(gym: str=DEFAULT_GYM, base_url: str=BASE_URL):
    """ Build the request URL
    :param gym: a gym pkg_id
    :param base_url: the base URL to make requests to
    :returns: full rockgympro URL
    """
    return f"{base_url}/{gym}/occupancy"


class GymData:
    """ Stores gym data parsed from the response. """
    def __init__(self, short_name: str, gym_info: dict):
        self.short_name = short_name
        self.gym_info = gym_info
        self.curr_occupancy = self.gym_info['count']
        self.capacity = self.gym_info['capacity']
        self.percent = 100.0 * (self.curr_occupancy / self.capacity)
        self.last_updated = self.gym_info['lastUpdate'].replace(NON_BREAK_SPACE, " ")
        


def load_gym_config() -> dict:
    """ Load the gym config """
    c = yaml.load(CONFIG_FILE, yaml.Loader)
    return c['gyms']

def build_gym_map(gym_config: List[dict]) -> dict:
    """ Gets map of (alternative names) -> (primary name, pkg id) """
    gym_name_map = {}
    for gym in gym_config:
        for alt in gym['alt']:
            gym_name_map[alt.lower()] = (gym['primary'], gym['pkg_id'])
    return gym_name_map

def get_all_gym_names() -> List[str]:
    """ Get all the gym alternative names """
    return list(build_gym_map(load_gym_config()).keys())

def get_all_gym_names_str() -> str:
    """ Get all the gym alternative names as a comma separated name """
    return ', '.join(get_all_gym_names())

@click.command()
@click.option('--gym',
              help=f"Specify a gym chain. Any of the following are acceptable: [{get_all_gym_names_str()}]",
              show_default=True,
              metavar="GYM",
              type=click.Choice(get_all_gym_names(), case_sensitive=False),
              default=DEFAULT_GYM)
def busyboulder(gym):

    gym_map = build_gym_map(load_gym_config())

    primary_chain_name, gym_pkg_id = gym_map.get(gym.lower(), None)
    if gym_pkg_id == None:
        click.Abort(f"{gym} is not valid!")

    headers = {
        'Accept' : '*/*',
        'Content-Type' : 'text/html; charset=UTF-8',
    }

    url = build_url(gym=gym_pkg_id)
    response = requests.get(url, headers=headers)

    html = response.text
    
    # Use Beautiful Soup to find the selector options
    soup = BeautifulSoup(html, 'html.parser')
    gym_switcher = soup.find(id='gym-switcher').find_all('option')

    # Construct a dict of short gym name -> human-readable name
    # e.g. POP -> Seattle Bouldering Project Popular
    gym_options = dict([(str(g['value']), str(g.text)) for g in gym_switcher if g['value'] != ""])

    # Use Beautiful Soup to find the scripts in the page
    # Find the 'var data = {...}' object which contains the useful info
    all_scripts = soup.find_all('script')
    gym_data = []
    for _, script in enumerate(all_scripts):
        if "var data = {" in script.text:
            # Find the data variable in script section

            pattern = re.compile(r"^\s+var data = ({.*},\s+});$", re.MULTILINE | re.DOTALL)
            match = pattern.match(script.text)
            if match == None:
                click.secho("No gyms found. Goodbye!", err=True)
                click.Abort()

            raw_data = match.groups()[0]
            data = ast.literal_eval(raw_data)
            for short_name, info in data.items():
                gym_data.append(GymData(short_name, info))

    for gym in gym_data:
        full_gym_name = gym_options.get(gym.short_name, "UNKNOWN")
        click.secho(f"{full_gym_name} ({gym.short_name})", bold=True)
        click.secho(f"Visitors: [{gym.curr_occupancy}], Capacity: [{gym.capacity}], [{gym.percent:.1f}%] full.")
        click.secho(f"Last updated: {gym.last_updated}")

if __name__ == "__main__":

    busyboulder()
