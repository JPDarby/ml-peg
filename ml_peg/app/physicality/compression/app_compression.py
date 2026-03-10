"""Run compression benchmark app."""

from __future__ import annotations

from ase.formula import Formula

from dash import Dash, dcc
from dash.dcc import Loading
from dash.html import Div, Label

from ml_peg.app import APP_ROOT
from ml_peg.app.base_app import BaseApp
from ml_peg.app.utils.build_callbacks import register_curve_gallery_callbacks
from ml_peg.models.get_models import get_model_names
from ml_peg.models.models import current_models

# Get all models
MODELS = get_model_names(current_models)
BENCHMARK_NAME = "Compression"
DATA_PATH = APP_ROOT / "data" / "physicality" / "compression"
CURVE_PATH = DATA_PATH / "curves"
DOCS_URL = (
    "https://ddmms.github.io/ml-peg/user_guide/benchmarks/"
    "physicality.html#compression"
)

# Relative URL prefix for serving structure .xyz files as Dash assets.
STRUCT_ASSET_PREFIX = "assets/physicality/compression/curves"

def _chemical_formula_from_label(label: str) -> str:
    """Convert a label like ``"C2H4_pyxtal_0"`` to a reduced formula ``"CH2"``."""
    formula_str = label.split("_")[0]
    f = Formula(formula_str)
    return str(f.reduce()[0])


# Subplot configuration: energy (symlog, eV) and pressure (symlog, GPa)
SUBPLOT_SPECS = [
    {
        "title": "Energy per atom vs Scale factor",
        "x_key": "scale",
        "y_key": "energy_per_atom",
        "y_label": "Energy per atom (eV, symlog)",
        "x_label": "Scale factor",
        "trace_prefix": "E",
        "hover_y_fmt": ".4f",
        "hover_y_unit": "eV",
        "symlog": {"linthresh": 10.0, "decades": 4, "linear_frac": 0.6},
    },
    {
        "title": "Pressure vs Scale factor",
        "x_key": "scale",
        "y_key": "pressure",
        "y_label": "Pressure (GPa, symlog)",
        "x_label": "Scale factor",
        "trace_prefix": "P",
        "hover_y_fmt": ".2f",
        "hover_y_unit": "GPa",
        "symlog": {"linthresh": 100.0, "decades": 4, "linear_frac": 0.6},
    },
]


class CompressionApp(BaseApp):
    """Compression benchmark app layout and callbacks."""

    def register_callbacks(self) -> None:
        """Register dropdown-driven compression curve callbacks."""
        register_curve_gallery_callbacks(
            model_dropdown_id=f"{BENCHMARK_NAME}-model-dropdown",
            group_dropdown_id=f"{BENCHMARK_NAME}-composition-dropdown",
            figure_id=f"{BENCHMARK_NAME}-figure",
            curve_dir=CURVE_PATH,
            group_fn=_chemical_formula_from_label,
            subplot_specs=SUBPLOT_SPECS,
            struct_container_id=f"{BENCHMARK_NAME}-struct-placeholder",
            struct_asset_prefix=STRUCT_ASSET_PREFIX,
        )


def get_app() -> CompressionApp:
    """
    Get compression benchmark app layout and callback registration.

    Returns
    -------
    CompressionApp
        Benchmark layout and callback registration.
    """
    model_options = [{"label": model, "value": model} for model in MODELS]
    default_model = model_options[0]["value"] if model_options else None

    extra_components = [
        Div(
            [
                Label("Select model:"),
                dcc.Dropdown(
                    id=f"{BENCHMARK_NAME}-model-dropdown",
                    options=model_options,
                    value=default_model,
                    clearable=False,
                    style={"width": "300px", "marginBottom": "20px"},
                ),
                Label("Select composition:"),
                dcc.Dropdown(
                    id=f"{BENCHMARK_NAME}-composition-dropdown",
                    options=[],
                    value=None,
                    clearable=False,
                    style={"width": "300px"},
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        Loading(
            dcc.Graph(
                id=f"{BENCHMARK_NAME}-figure",
                style={"height": "700px", "width": "100%", "marginTop": "20px"},
            ),
            type="circle",
        ),
        Div(
            "Click a point on a curve to view the structure.",
            id=f"{BENCHMARK_NAME}-struct-placeholder",
            style={"marginTop": "20px"},
        ),
    ]

    return CompressionApp(
        name=BENCHMARK_NAME,
        description=(
            "Uniform crystal compression explorer. Structures are isotropically "
            "scaled and the energy per atom, its derivative dE/dV, and stress are "
            "recorded. Metrics are averaged across all structures."
        ),
        docs_url=DOCS_URL,
        table_path=DATA_PATH / "compression_metrics_table.json",
        extra_components=extra_components,
    )


if __name__ == "__main__":
    dash_app = Dash(__name__, assets_folder=DATA_PATH.parent.parent)
    compression_app = get_app()
    dash_app.layout = compression_app.layout
    compression_app.register_callbacks()
    dash_app.run(port=8056, debug=True)
