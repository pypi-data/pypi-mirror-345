import os
from typing import Optional, Any

from algo_ops.ops.op import Op
from algo_ops.pipeline.pipeline import Pipeline
from ocr_ops.framework.op.abstract_ocr_op import EasyOCROp
from ocr_ops.framework.op.ffmpeg_op import FFMPEGOp
from ocr_ops.framework.pipeline.ocr_pipeline import OCRMethod
from ocr_ops.instances import ocr

from pokemon_card_recognizer.api.operating_mode import OperatingMode
from pokemon_card_recognizer.classifier.core.word_classifier import WordClassifier
from pokemon_card_recognizer.pulls_estimator.pulls_estimator import PullsEstimator
from pokemon_card_recognizer.pulls_estimator.pulls_summary import PullsSummary
from pokemon_card_recognizer.reference.core.build import ReferenceBuild


class CardRecognizer(Pipeline):
    def __init__(
        self,
        set_name: Optional[str] = "master",
        classification_method: str = "shared_words",
        mode: OperatingMode = OperatingMode.SINGLE_IMAGE,
        min_run_length: Optional[int] = 5,
        min_run_conf: Optional[float] = 0.1,
        run_tol: Optional[int] = 10,
    ):
        # load classifier
        ref_pkl_path = ReferenceBuild.get_set_pkl_path(set_name=set_name)
        self.classifier = WordClassifier(
            ref_pkl_path=ref_pkl_path,
            vect_method="encapsulation_match",
            classification_method=classification_method,
        )

        # load OCR pipeline
        if mode in [
            OperatingMode.IMAGE_DIR,
            OperatingMode.VIDEO,
            OperatingMode.PULLS_IMAGE_DIR,
            OperatingMode.PULLS_VIDEO,
            OperatingMode.BOOSTER_PULLS_IMAGE_DIR,
            OperatingMode.BOOSTER_PULLS_VIDEO,
        ]:
            store_intermediate_images = False
        else:
            store_intermediate_images = True
        self.ocr_pipeline = ocr.basic_ocr_with_text_cleaning_pipeline(
            vocab_words=self.classifier.reference.vocab(),
            ocr_method=OCRMethod.EASYOCR,
            store_intermediate_images=store_intermediate_images,
        )

        # make pipeline
        if mode == OperatingMode.VIDEO:
            ops = [FFMPEGOp(), self.ocr_pipeline, self.classifier]
        elif mode == OperatingMode.SINGLE_IMAGE:
            ops = [
                self.ocr_pipeline,
                self.classifier,
            ]
        elif mode == OperatingMode.IMAGE_DIR:
            ops = [
                self.ocr_pipeline,
                self.classifier,
            ]
        elif mode == OperatingMode.PULLS_IMAGE_DIR:
            ops = [
                self.ocr_pipeline,
                self.classifier,
                PullsEstimator(
                    min_run_length=min_run_length,
                    min_run_conf=min_run_conf,
                    run_tol=run_tol,
                    num_cards_to_select=None,
                ),
                PullsSummary(operating_mode=mode),
            ]
        elif mode == OperatingMode.PULLS_VIDEO:
            ops = [
                FFMPEGOp(),
                self.ocr_pipeline,
                self.classifier,
                PullsEstimator(
                    min_run_length=min_run_length,
                    min_run_conf=min_run_conf,
                    run_tol=run_tol,
                    num_cards_to_select=None,
                    figs_paging=True,
                ),
                PullsSummary(operating_mode=mode),
            ]
        elif mode == OperatingMode.BOOSTER_PULLS_IMAGE_DIR:
            ops = [
                self.ocr_pipeline,
                self.classifier,
                PullsEstimator(
                    min_run_length=min_run_length,
                    min_run_conf=min_run_conf,
                    run_tol=run_tol,
                ),
                PullsSummary(operating_mode=mode),
            ]
        elif mode == OperatingMode.BOOSTER_PULLS_VIDEO:
            ops = [
                FFMPEGOp(),
                self.ocr_pipeline,
                self.classifier,
                PullsEstimator(
                    min_run_length=min_run_length,
                    min_run_conf=min_run_conf,
                    run_tol=run_tol,
                ),
                PullsSummary(operating_mode=mode),
            ]
        else:
            raise ValueError("Unsupported mode: " + str(mode))
        super().__init__(ops=ops)

    def find_op_by_class(self, op_class: Any) -> Optional[Op]:
        for op in self.ops.values():
            if isinstance(op, op_class):
                return op
        return None

    def set_output_path(self, output_path: Optional[str] = None):
        """
        Set output path for results.
        """
        ffmpeg_op = self.find_op_by_class(op_class=FFMPEGOp)
        if ffmpeg_op is not None:
            ffmpeg_op.image_out_path = os.path.join(
                output_path, "uncompressed_video_frames"
            )
        pulls_estimator_op = self.find_op_by_class(op_class=PullsEstimator)
        if pulls_estimator_op is not None:
            pulls_estimator_op.output_fig_path = output_path
        autosave_path = os.path.join(output_path, "ocr_bounding_boxes")
        self.ocr_pipeline.ocr_op.autosave_output_img_path = autosave_path

    def set_summary_file(self, summary_file: str):
        """
        Set summary file.
        """
        pulls_summary_op = self.find_op_by_class(op_class=PullsSummary)
        if pulls_summary_op is None:
            raise ValueError("There is no pulls summary op found in this pipeline.")
        if pulls_summary_op is not None:
            pulls_summary_op.summary_file = summary_file

    def to_pickle(self, out_pkl_path: str, compression: Optional[str] = None) -> None:
        # temporarily remove un-pickleable elements
        easy_ocr_instance = None
        if isinstance(self.ocr_pipeline.ocr_op, EasyOCROp):
            easy_ocr_instance = self.ocr_pipeline.ocr_op.easy_ocr_reader
            self.ocr_pipeline.ocr_op.easy_ocr_reader = None

        # super call to pickle
        super().to_pickle(out_pkl_path=out_pkl_path, compression=compression)

        # restore state
        if isinstance(self.ocr_pipeline.ocr_op, EasyOCROp):
            self.ocr_pipeline.ocr_op.easy_ocr_reader = easy_ocr_instance
