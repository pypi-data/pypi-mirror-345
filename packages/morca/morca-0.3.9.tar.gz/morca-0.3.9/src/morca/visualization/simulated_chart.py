import altair as alt
import numpy as np
import polars as pl

from morca.processing import apply_gaussian_convolution, compute_total_spectrum


def create_simulated_spectrum_chart(
    bar_spectrum: pl.DataFrame,
    fwhm: float,
    energy_column: str = "energy_cm",
    intensity_column: str = "fosc",
    name_column: str = "to_state",
    grid_points: int = 500,
    grid_domain: tuple[float, float] = (0, 60_000),
) -> alt.Chart | alt.LayerChart:
    grid = np.linspace(*grid_domain, grid_points)
    _gaussians, _grid = apply_gaussian_convolution(
        bar_spectrum, fwhm, energy_column, intensity_column, name_column, grid=grid
    )
    _simulated_spectrum_df = compute_total_spectrum(_gaussians, _grid)

    # Combine all gaussians into a single dataframe
    combined_gaussians = pl.concat(_gaussians)

    individual_chart = (
        alt.Chart(combined_gaussians)
        .mark_area(opacity=0.3)
        .encode(
            x=energy_column,
            y=alt.Y(intensity_column, stack=None),
            color=alt.Color(f"{name_column}:N").scale(
                scheme="category20", domain=range(0, 128)
            ),
        )
    )

    # Create a chart for the sum
    sum_chart = (
        alt.Chart(_simulated_spectrum_df)
        .mark_line()
        .encode(
            x=alt.X(energy_column, scale=dict(domain=grid_domain)), y=intensity_column
        )
    )

    # Layer the individual gaussians with the sum
    final_chart = alt.layer(individual_chart, sum_chart).resolve_scale(
        color="independent"
    )

    return final_chart
