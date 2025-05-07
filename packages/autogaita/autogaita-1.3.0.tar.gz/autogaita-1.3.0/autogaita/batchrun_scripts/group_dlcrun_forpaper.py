import autogaita


def group_dlcrun():
    """
    Batchrun script to run AutoGaitA Group for Results obtained with AutoGaitA DLC.
    folderinfo & cfg dictionaries must be configured as explained in our documentation. See the "AutoGaitA without the GUI" section of our documentation for references to in-depth explanations to all dictionary keys (note that each key of dicts corresponds to some object in the AutoGaitA Group GUI)
    """

    # ----------------------------- 3 Months 3 Beams --------------------------------
    # folderinfo = {}
    # folderinfo["group_names"] = [
    #     # RM Dataset
    #     "3m_5mm",
    #     "3m_12mm",
    #     "3m_25mm",
    # ]
    # folderinfo["group_dirs"] = [
    #     "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/5mm/9w/",
    #     "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/12mm/9w/",
    #     "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/25mm/9w/",
    # ]
    # folderinfo["results_dir"] = (
    #     "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/3Months3BeamsForPaper"

    # ----------------------------- Old Young 3 Beams --------------------------------
    folderinfo = {}
    folderinfo["group_names"] = [
        # RM Dataset
        "3m_5mm",
        "3m_12mm",
        "3m_25mm",
        "24m_5mm",
        "24m_12mm",
        "24m_25mm",
    ]
    folderinfo["group_dirs"] = [
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/5mm/9w/",
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/12mm/9w/",
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/25mm/9w/",
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/5mm/104w/",
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/12mm/104w/",
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/255mm/104w/",
    ]
    folderinfo["results_dir"] = (
        "/Users/mahan/sciebo/Research/AutoGaitA/Mouse/Full Dataset and Results Nov 2024/YoungOld3BeamsForPaper_v2"
    )
    folderinfo["load_dir"] = ""

    # cfg
    cfg = {}
    cfg["do_permtest"] = False
    cfg["do_anova"] = True
    cfg["permutation_number"] = 10000
    cfg["PCA_n_components"] = 3
    # cfg["PCA_n_components"] = 0.33
    # cfg["PCA_custom_scatter_PCs"] = "4,5,6;4,5;2,4,6"
    cfg["PCA_custom_scatter_PCs"] = ""
    cfg["PCA_save_3D_video"] = False  # True
    cfg["PCA_bins"] = ""  # "0-10,24,50-75"
    cfg["stats_threshold"] = 0.05
    cfg["plot_SE"] = True
    cfg["color_palette"] = "Set2"
    cfg["dont_show_plots"] = True
    cfg["legend_outside"] = True
    cfg["which_leg"] = "left"
    cfg["anova_design"] = "RM ANOVA"
    cfg["PCA_variables"] = [
        "Nose x",
        "Nose y",
        "Ear base x",
        "Ear base y",
        "Front paw tao x",
        "Front paw tao y",
        "Wrist x",
        "Wrist y",
        "Elbow x",
        "Elbow y",
        "Lower Shoulder x",
        "Lower Shoulder y",
        "Upper Shoulder x",
        "Upper Shoulder y",
        "Iliac Crest x",
        "Iliac Crest y",
        "Hip x",
        "Hip y",
        "Knee x",
        "Knee y",
        "Ankle x",
        "Ankle y",
        "Hind paw tao x",
        "Hind paw tao y",
        "Tail base y",
        "Tail center x",
        "Tail center y",
        "Tail tip x",
        "Tail tip y",
        "Hind paw tao Velocity",
        "Hind paw tao Acceleration",
        "Ankle Velocity",
        "Ankle Acceleration",
        "Knee Velocity",
        "Knee Acceleration",
        "Hip Velocity",
        "Hip Acceleration",
        "Iliac Crest Velocity",
        "Iliac Crest Acceleration",
        "Ankle Angle",
        "Knee Angle",
        "Hip Angle",
        "Wrist Angle",
        "Elbow Angle",
        "Lower Shoulder Angle",
        "Iliac Crest Angle",
        "Ankle Angle Velocity",
        "Ankle Angle Acceleration",
        "Knee Angle Acceleration",
        "Hip Angle Velocity",
        "Hip Angle Acceleration",
        "Wrist Angle Velocity",
        "Wrist Angle Acceleration",
        "Elbow Angle Velocity",
        "Elbow Angle Acceleration",
        "Lower Shoulder Angle Velocity",
        "Lower Shoulder Angle Acceleration",
        "Iliac Crest Angle Velocity",
        "Iliac Crest Angle Acceleration",
    ]
    cfg["stats_variables"] = [
        "Hip x",
        "Hip y",
        "Knee x",
        "Knee y",
        "Ankle x",
        "Ankle y",
        "Hind paw tao x",
        "Hind paw tao y",
        "Hind paw tao Velocity",
        "Ankle Velocity",
        "Knee Velocity",
        "Ankle Angle",
        "Knee Angle",
        "Hip Angle",
    ]
    # run
    autogaita.group(folderinfo, cfg)


# %% what happens if we just hit run
if __name__ == "__main__":
    group_dlcrun()
