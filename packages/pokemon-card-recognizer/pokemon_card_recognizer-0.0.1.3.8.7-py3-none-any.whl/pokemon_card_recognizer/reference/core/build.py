import os
import random
import sys
from typing import List, Dict

import ezplotly.settings as plot_settings
from ordered_set import OrderedSet
from pokemontcgsdk import Card, Set

from pokemon_card_recognizer.classifier.core.card_prediction_result import (
    CardPrediction,
)
from pokemon_card_recognizer.classifier.core.word_classifier import WordClassifier
from pokemon_card_recognizer.infra.ptcgsdk.ptcgsdk import (
    query_set_cards,
    download_card_images,
    init_api,
)
from pokemon_card_recognizer.reference.core.card_reference import CardReference
from pokemon_card_recognizer.reference.eval.plots import (
    plot_word_counts,
    plot_classifier_sensitivity_curve,
)


class ReferenceBuild:
    @staticmethod
    def supported_card_sets() -> OrderedSet[str]:
        """
        Get list of supported set names.
        """
        card_sets = OrderedSet([s.name for s in Set.all()])
        return card_sets

    @staticmethod
    def get_path_to_data() -> str:
        """
        Get path to top-level sample_data folder for reference build.
        """
        data_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "data"
        )
        return data_folder

    @staticmethod
    def get_path() -> str:
        """
        Get path to reference build folder.
        """
        return os.path.join(ReferenceBuild.get_path_to_data(), "ref_build")

    @staticmethod
    def get_set_pkl_path(set_name: str) -> str:
        """
        Get path to reference build pickle file for set. Throws a value error if file does not exist.

        param: set_name

        return:
            Path to ref build pickle file for set
        """
        pkl_file = set_name.lower().replace(" ", "_") + ".pkl"
        full_path = os.path.join(ReferenceBuild.get_path(), pkl_file)
        if not os.path.exists(full_path):
            raise ValueError(
                "Reference build not found for set: "
                + str(set_name)
                + ". Has reference been setup? If not, run build.py."
            )
        return full_path

    @staticmethod
    def get(set_name: str) -> CardReference:
        """
        Loads or obtains a pre-cached version of set reference.

        param set_name: The set to get

        Return:
            Set Card Reference
        """
        if set_name not in ReferenceBuild.supported_card_sets() | {"Master", "master"}:
            raise ValueError("Not a supported card reference set: " + str(set_name))
        if not hasattr(ReferenceBuild, "loaded_references"):
            ReferenceBuild.loaded_references = dict()
        if set_name not in ReferenceBuild.loaded_references:
            ReferenceBuild.loaded_references[set_name] = ReferenceBuild._load(
                set_name=set_name
            )
        return ReferenceBuild.loaded_references[set_name]

    @staticmethod
    def lookup(card_prediction: CardPrediction) -> Card:
        """
        Lookup card in reference.

        param card_prediction: The card prediction to lookup

        Return:
            Card object
        """
        card_ref = ReferenceBuild.get(set_name=card_prediction.reference_name)
        return card_ref.lookup_card_prediction(card_prediction=card_prediction)

    @staticmethod
    def _load(set_name: str) -> CardReference:
        """
        Load built reference for set.

        param set_name: The set to load

        Return:
            Set Card Reference
        """
        ref_build_path = ReferenceBuild.get_set_pkl_path(set_name=set_name)
        return CardReference.load_from_pickle(
            pkl_path=ref_build_path, compression="lzma"
        )

    @staticmethod
    def load_all_card_references() -> Dict[str, CardReference]:
        """
        Load all card reference objects.

        Returns:
            Dict mapping set name to CardReference object for set
        """
        return {
            set_name: ReferenceBuild._load(set_name=set_name)
            for set_name in ReferenceBuild.supported_card_sets()
        }

    @staticmethod
    def build(ptcgsdk_api_key: str, download_images: bool = True) -> None:
        """
        Downloads images and builds reference for all card sets.

        param ptcgsdk_api_key: The API key for PTCGSDK
        param download_images: Whether to download images (or skip if already downloaded)
        """

        # init pokemon sdk API
        init_api(api_key=ptcgsdk_api_key)

        # loop over sets to build set-specific references
        master_set: List[Card] = list()
        for set_name in ReferenceBuild.supported_card_sets():
            # extract set prefix and specify output path
            set_prefix = set_name.lower().replace(" ", "_")
            out_pkl_path = os.path.join(ReferenceBuild.get_path(), set_prefix + ".pkl")

            # If reference already built, skip it. Allows recovery from failure.
            if os.path.exists(out_pkl_path):
                print("Skipping " + set_prefix)
                continue

            # query cards in set
            print(set_name + ": Querying set...")
            cards = query_set_cards(set_name=set_name)
            master_set += cards

            # download card images
            if download_images:
                out_images_path = os.path.join(
                    ReferenceBuild.get_path_to_data(), "card_images", set_prefix
                )
                print(set_name + ": Downloading images...")
                download_card_images(cards=cards, out_path=out_images_path)

            # build card text reference pickle file
            print(set_name + ": building reference...")
            os.makedirs(
                os.path.join(ReferenceBuild.get_path()),
                exist_ok=True,
            )
            reference = CardReference(cards=cards, name=set_name)
            reference.to_pickle(out_pkl_path=out_pkl_path, compression="lzma")

        # build master reference
        print("Building master reference...")
        out_pkl_path = os.path.join(ReferenceBuild.get_path(), "master.pkl")
        if os.path.exists(out_pkl_path):
            print("Skipping master")
        else:
            master_reference = CardReference(cards=master_set, name="master")
            master_reference.to_pickle(out_pkl_path=out_pkl_path, compression="lzma")

    @staticmethod
    def make_eval_plots() -> None:
        """
        Makes all evaluation plots.
        """

        print("Making Eval plots...")
        eval_plots_dir = os.path.join(ReferenceBuild.get_path_to_data(), "eval_figs")
        os.makedirs(eval_plots_dir, exist_ok=True)
        print("Plotting word counts..")
        plot_word_counts(
            references=ReferenceBuild.load_all_card_references(),
            outfile=os.path.join(eval_plots_dir, "word_counts.png"),
        )
        for classifier_method in WordClassifier.get_supported_classifier_methods():
            print(
                "Plotting sensitivity curve for classifier_method: "
                + str(classifier_method)
            )
            plot_classifier_sensitivity_curve(
                set_pkl_paths={
                    set_name: ReferenceBuild.get_set_pkl_path(set_name)
                    for set_name in (ReferenceBuild.supported_card_sets() | {"Master"})
                },
                classifier_method=classifier_method,
                outfile=os.path.join(
                    eval_plots_dir, classifier_method + "_sensitivity_curve.png"
                ),
            )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USAGE: python build.py [PTCGSDK_API_KEY]")
    else:
        # setup
        run_eval: bool = True
        plot_settings.SUPPRESS_PLOTS = True
        random.seed(0)

        # build reference
        ptcgsdk_api_key_val = sys.argv[0]
        ReferenceBuild.build(
            ptcgsdk_api_key=ptcgsdk_api_key_val, download_images=run_eval
        )

        # evaluate plots
        if run_eval:
            ReferenceBuild.make_eval_plots()
