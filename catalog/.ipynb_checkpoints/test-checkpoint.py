import sys
sys.path.append("/home/zrn/Workspace/")

from sbplan.catalog import CometCatalog

def test():
    """
    """

    try:

        # Update catalog
        print("Try to update an individual catalog.")
        CometCatalog.update("obs", verbose=True)

        # Load a downloaded catalog
        print("Try to load a downloaded catalog")
        comet_obs_catalog = CometCatalog.get("obs", update=False)
        print(comet_obs_catalog)

        # Download and then load a catalog
        print("Try to download and then load a catalog")
        comet_obs_catalog = CometCatalog.get("obs", update=True)
        print(comet_obs_catalog)

#         # Load a list of downloaded catalogs
#         print("Try to load a list of downloaded catalogs")
#         comet_all_catalog, comet_obs_catalog = CometCatalog.get(["all", "obs"], update=False)
#         print(comet_all_catalog, comet_obs_catalog)

#         # Download and then load a list of catalogs
#         print("Try to download and then load a list of catalogs")
#         comet_all_catalog, comet_obs_catalog = CometCatalog.get(["all", "obs"], update=True)
#         print(comet_obs_catalog)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    test()