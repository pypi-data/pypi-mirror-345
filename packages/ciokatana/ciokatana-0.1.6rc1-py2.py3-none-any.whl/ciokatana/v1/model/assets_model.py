import re
from Katana import NodegraphAPI, AssetAPI, FarmAPI
from ciokatana.v1.model import array_model

from ciokatana.v1 import const as k
from ciokatana.v1.model.asset_scraper import AssetScraper
from ciopath.gpath_list import PathList


PARAM = "extraAssets"


def create(node):
    """Create the project parameter and internal node."""
    params = node.getParameters()

    params.createChildStringArray(PARAM, 0)


def get_entries(node):
    return array_model.get_entries(node, PARAM)


def set_entries(node, entries):
    array_model.set_entries(node, PARAM, entries)


def scrape_assets():
    """Scan the nodegraph for assets."""
    scraper = AssetScraper()
    scraper.scrape()
    return scraper.get_path_list()


def resolve(node):
    projectfile = NodegraphAPI.NodegraphGlobals.GetProjectFile()
    if not projectfile:
        projectfile = k.NOT_SAVED
    path_list = PathList(projectfile)

    extra_assets = get_entries(node)
    path_list.add(*extra_assets)

    scraped_assets = scrape_assets()
    path_list.add(*scraped_assets)

    path_list.real_files()

    return {
        "upload_paths": [p.fslash() for p in path_list],
    }
