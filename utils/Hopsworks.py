from consts import FW_VERSION, FG_VERSION


def get_football_featureview(fs):
    try:
        feature_view = fs.get_feature_view(name="fw_football", version=FW_VERSION)
    except:
        fg_football = fs.get_feature_group(name="fg_football", version=FG_VERSION)
        query = fg_football.select_all()
        feature_view = fs.create_feature_view(name="fw_football",
                                              version=FW_VERSION,
                                              description="Read from football dataset",
                                              query=query)
    return feature_view
