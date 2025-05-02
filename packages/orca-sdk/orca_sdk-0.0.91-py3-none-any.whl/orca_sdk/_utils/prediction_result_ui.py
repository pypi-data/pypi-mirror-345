import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import gradio as gr

from ..memoryset import LabeledMemoryLookup

if TYPE_CHECKING:
    from ..telemetry import LabelPrediction


def inspect_prediction_result(prediction_result: "LabelPrediction"):
    label_names = prediction_result.memoryset.label_names

    def update_label(val: str, memory: LabeledMemoryLookup, progress=gr.Progress(track_tqdm=True)):
        progress(0)
        match = re.search(r".*\((\d+)\)$", val)
        if match:
            progress(0.5)
            new_label = int(match.group(1))
            memory.update(label=new_label)
            progress(1)
            return "&#9989; Changes saved"
        else:
            logging.error(f"Invalid label format: {val}")

    with gr.Blocks(
        fill_width=True,
        title="Prediction Results",
        css_paths=str(Path(__file__).parent / "prediction_result_ui.css"),
    ) as prediction_result_ui:
        gr.Markdown("# Prediction Results")
        gr.Markdown(f"**Input:** {prediction_result.input_value}")
        gr.Markdown(f"**Prediction:** {label_names[prediction_result.label]} ({prediction_result.label})")
        gr.Markdown("### Memory Lookups")

        with gr.Row(equal_height=True, variant="panel"):
            with gr.Column(scale=7):
                gr.Markdown("**Value**")
            with gr.Column(scale=3, min_width=150):
                gr.Markdown("**Label**")
        for i, mem_lookup in enumerate(prediction_result.memory_lookups):
            with gr.Row(equal_height=True, variant="panel", elem_classes="white" if i % 2 == 0 else None):
                with gr.Column(scale=7):
                    gr.Markdown(
                        (
                            mem_lookup.value
                            if isinstance(mem_lookup.value, str)
                            else "Time series data"
                            if isinstance(mem_lookup.value, list)
                            else "Image data"
                        ),
                        label="Value",
                        height=50,
                    )
                with gr.Column(scale=3, min_width=150):
                    dropdown = gr.Dropdown(
                        choices=[f"{label_name} ({i})" for i, label_name in enumerate(label_names)],
                        label="Label",
                        value=f"{label_names[mem_lookup.label]} ({mem_lookup.label})",
                        interactive=True,
                        container=False,
                    )
                    changes_saved = gr.HTML(lambda: "", elem_classes="success no-padding", every=15)
                    dropdown.change(
                        lambda val, mem_lookup=mem_lookup: update_label(val, mem_lookup),
                        inputs=[dropdown],
                        outputs=[changes_saved],
                        show_progress="full",
                    )

    prediction_result_ui.launch()
