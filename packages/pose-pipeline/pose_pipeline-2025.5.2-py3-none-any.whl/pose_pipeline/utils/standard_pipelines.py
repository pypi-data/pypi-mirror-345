from pose_pipeline import *
from pose_pipeline.utils.tracking import annotate_single_person
from typing import List, Dict, Union


def find_lifting_keys(filt=None):
    return ((Video - LiftingPerson) & filt).fetch("KEY")


def tracking_pipeline(
    keys: Union[Dict, List[Dict]],
    tracking_method_name: str = "MMDet_deepsort",
    reserve_jobs: bool = False,
):
    """
    Run pipeline on a video through to the tracking layer.

    Args:
        key (dict)                   : key to compute
        tracking_method_name (str)   : tracking method of PersonBbox to use to identify person
        reserve_jobs (bool)          : whether to reserve jobs or not
    """

    if isinstance(keys, dict):
        keys = [keys]

    tracking_keys = []

    for key in keys:
        # compute some necessary statistics
        VideoInfo.populate(key, reserve_jobs=reserve_jobs)

        # set up and compute tracking method
        tracking_key = key.copy()
        tracking_method = (TrackingBboxMethodLookup & f'tracking_method_name="{tracking_method_name}"').fetch1(
            "tracking_method"
        )
        tracking_key["tracking_method"] = tracking_method
        TrackingBboxMethod.insert1(tracking_key, skip_duplicates=True)
        TrackingBbox.populate(tracking_key, reserve_jobs=reserve_jobs)

        # see if it can be automatically annotated
        annotate_single_person(key)

        # compute the person bbox (requires a method to have inserted the valid bbox)
        PersonBbox.populate(tracking_key, reserve_jobs=True)

        DetectedFrames.populate(tracking_key, reserve_jobs=reserve_jobs)

        if len(PersonBbox & tracking_key) == 1:
            tracking_keys.append((PersonBbox & tracking_key).fetch1("KEY"))

    return tracking_keys


def top_down_pipeline(
    key: Union[Dict, List[Dict]],
    tracking_method_name: str = "MMDet_deepsort",
    top_down_method_name: str = "MMpose",
    reserve_jobs: bool = False,
):
    """
    Run pipeline on a video through to the top down person layer.

    Args:
        key (dict)                  : key or keys to compute
        tracking_method_name (str)  : tracking method of PersonBbox to use to identify person
        top_down_method_name (str)  : top down method of TopDownPerson to use to identify person
        reserve_jobs (bool)          : whether to reserve jobs or not
    """

    tracking_keys = tracking_pipeline(key, tracking_method_name, reserve_jobs=reserve_jobs)
    top_down_person_keys = []

    for tracking_key in tracking_keys:
        # compute the person bbox (requires a method to have inserted the valid bbox)
        PersonBbox.populate(tracking_key, reserve_jobs=True)

        if len(PersonBbox & tracking_key) == 0:
            if (
                len(PersonBboxValid & tracking_key) == 1
                and (PersonBboxValid & tracking_key).fetch1("video_subject_id") < 0
            ):
                print(f"Video {key} marked as invalid.")
                return False
            print(f"Waiting for annotation of subject of interest. {tracking_key}")
            return False

        # compute top down person
        top_down_key = (PersonBbox & tracking_key).fetch1("KEY")
        top_down_method = (TopDownMethodLookup & f'top_down_method_name="{top_down_method_name}"').fetch1(
            "top_down_method"
        )
        top_down_key["top_down_method"] = top_down_method
        TopDownMethod.insert1(top_down_key, skip_duplicates=True)
        if top_down_method_name == "OpenPose":
            OpenPose.populate(key)
            OpenPosePerson.populate(key)

        TopDownPerson.populate(top_down_key, reserve_jobs=reserve_jobs)

        # TODO: probably should remove this but make sure it doesn't break anything
        BestDetectedFrames.populate(key, reserve_jobs=reserve_jobs)

        top_down_person_keys.append(top_down_key)

    return top_down_person_keys


def lifting_pipeline(
    key,
    tracking_method_name: str = "MMDet_deepsort",
    top_down_method_name: str = "Bridging_bml_movi_87",
    lifting_method_name: str = "Bridging_bml_movi_87",
    reserve_jobs: bool = False,
):
    """
    Run pipeline on a video through to the  lifting layer.

    Args:
        key (dict)                  : key to compute
        tracking_method_name (str)  : tracking method of PersonBbox to use to identify person
        top_down_method_name (str)  : top down method of TopDownPerson to use to identify person
        lifting_method_name (str)   : lifting method of LiftingPerson to use to identify person

    Returns:
        bool: whether the pipeline was successful or not
    """

    res = top_down_pipeline(key, tracking_method_name, top_down_method_name, reserve_jobs=reserve_jobs)
    if not res:
        return res

    tracking_key = key.copy()
    tracking_method = (TrackingBboxMethodLookup & f'tracking_method_name="{tracking_method_name}"').fetch1(
        "tracking_method"
    )
    tracking_key["tracking_method"] = tracking_method

    top_down_key = (PersonBbox & tracking_key).fetch1("KEY")
    top_down_method = (TopDownMethodLookup & f'top_down_method_name="{top_down_method_name}"').fetch1("top_down_method")
    top_down_key["top_down_method"] = top_down_method

    if len(TopDownPerson & top_down_key) == 0:
        print(f"Top down job must be reserved and not completed. {top_down_key}")
        return False

    # compute lifting
    lifting_key = top_down_key.copy()
    lifting_method = (LiftingMethodLookup & f'lifting_method_name="{lifting_method_name}"').fetch1("lifting_method")
    lifting_key["lifting_method"] = lifting_method
    LiftingMethod.insert1(lifting_key, skip_duplicates=True)
    LiftingPerson.populate(key, reserve_jobs=reserve_jobs)

    if len(LiftingPerson & lifting_key) == 0:
        print(f"Lifting job must be reserved and not completed. {lifting_key}")
        return False

    # compute some necessary statistics
    VideoInfo.populate(key, reserve_jobs=reserve_jobs)
    DetectedFrames.populate(key, reserve_jobs=reserve_jobs)
    BestDetectedFrames.populate(key, reserve_jobs=reserve_jobs)

    return len(LiftingPerson & key) > 0


def smpl_pipeline(
    key: Union[Dict, List[Dict]],
    tracking_method_name: str = "DeepSortYOLOv4",
    smpl_method_name: str = "PIXIE",
    reserve_jobs: bool = False,
):
    """
    Run pipeline on a video through to the  lifting layer.

    Args:
        key (dict or list of dict)  : key or keys to compute
        tracking_method_name (str)  : tracking method of PersonBbox to use to identify person
        smpl_method_name (str)      : smpl method of SMPLPerson to use to identify person
        lifting_method_name (str)   : lifting method of LiftingPerson to use to identify person

    Returns:
        list of dict: keys of SMPLPerson that were computed
    """

    tracking_keys = tracking_pipeline(key, tracking_method_name, reserve_jobs=reserve_jobs)
    smpl_keys = []
    for key in tracking_keys:
        if len(PersonBbox & key) == 0:
            if len(PersonBboxValid & key) == 1 and (PersonBboxValid & key).fetch1("video_subject_id") < 0:
                print(f"Video {key} marked as invalid.")
                return False
            print(f"Waiting for annotation of subject of interest. {key}")
            return False

        # compute SMPL
        smpl_key = key.copy()
        smpl_method = (SMPLMethodLookup & f'smpl_method_name="{smpl_method_name}"').fetch1("smpl_method")
        smpl_key["smpl_method"] = smpl_method
        SMPLMethod.insert1(smpl_key, skip_duplicates=True)
        SMPLPerson.populate(smpl_key, reserve_jobs=reserve_jobs)

        if len(SMPLPerson & smpl_key) == 1:
            smpl_keys.append(smpl_key)

    return smpl_keys


def bottomup_to_topdown(
    keys: Union[Dict, List[Dict]],
    bottom_up_method_name: str = "OpenPose_BODY25B",
    tracking_method_name: str = "DeepSortYOLOv4",
    reserve_jobs: bool = False,
):
    """
    Compute a BottomUp person and migrate to top down table

    This doesn't stick exactly to DataJoint design patterns, but
    combines a PersonBbox and BottomUp method and then creates a
    TopDownPerson that migrates this data over.

    Args:
        keys (list of dict)         : keys to compute
        bottom_up_method_name (str) : should match BottomUpMethod and TopDownMethod
        tracking_method_name (str)  : tracking method of PersonBbox to use to identify person
        reserve_jobs (bool)         : whether to reserve jobs or not
    """

    results = []
    if type(keys) == dict:
        keys = list(keys)

    for key in keys:
        key = key.copy()

        # get this here to confirm it will work below
        bbox_key = (
            PersonBbox & key & (TrackingBboxMethodLookup & {"tracking_method_name": tracking_method_name})
        ).fetch1("KEY")

        if bottom_up_method_name in ["Bridging_COCO_25", "Bridging_bml_movi_87"]:
            from pose_pipeline.pipeline import BottomUpBridging, BottomUpBridgingPerson

            BottomUpBridging.populate(key, reserve_jobs=reserve_jobs)
            BottomUpBridgingPerson.populate(bbox_key, reserve_jobs=reserve_jobs)

            if len(BottomUpBridgingPerson & bbox_key) == 0:
                print(f"BottomUpBridgingPerson job must be reserved and not completed. {bbox_key}")
                continue

        else:
            # compute bottom up method for this video
            key["bottom_up_method_name"] = bottom_up_method_name
            BottomUpMethod.insert1(key, skip_duplicates=True)
            BottomUpPeople.populate(key, reserve_jobs=reserve_jobs)

            # use the desired tracking method to identify the person
            key["tracking_method"] = (TrackingBboxMethodLookup & {"tracking_method_name": tracking_method_name}).fetch1(
                "tracking_method"
            )
            BottomUpPerson.populate(key, reserve_jobs=reserve_jobs)

            if len(BottomUpPerson & key) == 0:
                print(f"BottomUpPerson job must be reserved and not completed. {key}")
                continue

        bbox_key["top_down_method"] = (TopDownMethodLookup & {"top_down_method_name": bottom_up_method_name}).fetch1(
            "top_down_method"
        )
        TopDownMethod.insert1(bbox_key, skip_duplicates=True)
        TopDownPerson.populate(bbox_key, reserve_jobs=reserve_jobs)


def bottom_up_pipeline(
    keys: Union[Dict, List[Dict]], bottom_up_method_name: str = "OpenPose_HR", reserve_jobs: bool = False
):
    """
    Run bottom up method on a video

    Args:
        keys (list) : list of keys (dict) to run bottom up on
        bottom_up_method_name (str) : should match BottomUpMethod and TopDownMethod
        reserve_jobs (bool) : whether to reserve jobs or not
    """

    if type(keys) == dict:
        keys = [keys]

    for key in keys:
        key = key.copy()

        if bottom_up_method_name in ["Bridging_COCO_25", "Bridging_bml_movi_87", "Bridging_OpenPose"]:
            from pose_pipeline.pipeline import BottomUpBridging

            print(f"Computing {bottom_up_method_name} for {key}")

            BottomUpBridging.populate(key, reserve_jobs=reserve_jobs)

            if len(BottomUpBridging & key) == 0:
                print(f"Bottom up job must be reserved and not completed. Skipping {key}")
                continue

            # migrate those results to BottomUpPeople
            key = (Video & key).fetch1("KEY")
            key["bottom_up_method_name"] = bottom_up_method_name
            BottomUpMethod.insert1(key, skip_duplicates=True)
            BottomUpPeople.populate(key, reserve_jobs=reserve_jobs)
            print(f"Computed {bottom_up_method_name} for {key}")

        else:
            # compute bottom up method for this video
            key["bottom_up_method_name"] = bottom_up_method_name
            BottomUpMethod.insert1(key, skip_duplicates=True)
            BottomUpPeople.populate(key, reserve_jobs=reserve_jobs)


def blur_videos(keys: Union[Dict, List[Dict]], reserve_jobs: bool = False):
    """
    Run blurring on a video

    Args:
        keys (list) : list of keys (dict) to run bottom up on
        reserve_jobs (bool) : whether to reserve jobs or not
    """

    # required for blurring, which is required for annotation

    if type(keys) == dict:
        print("keys is a dict")
        keys = [keys]

    for key in keys:
        print(key)

        VideoInfo.populate(key, reserve_jobs=reserve_jobs)  # required for various downstream tasks
        bottom_up_pipeline(key, bottom_up_method_name="Bridging_OpenPose", reserve_jobs=reserve_jobs)

        # handle the case where some of the jobs where reserved
        if len(BottomUpPeople & key) > 0:
            BlurredVideo.populate(key, reserve_jobs=reserve_jobs)
