# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "altair==5.5.0",
#     "cotwo==1.1.10",
#     "marimo",
#     "morca==0.3.1",
#     "polars==1.28.1",
# ]
# ///

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from pathlib import Path

    import polars as pl
    import altair as alt
    import cotwo

    from morca import OrcaOutput
    from morca.visualization import create_simulated_spectrum_chart
    return OrcaOutput, Path, cotwo, create_simulated_spectrum_chart, pl


@app.cell
def _(mo):
    file_text = mo.ui.text(
        label="Path to output file",
        value="/Users/freddy/Documents/Projects/morca/test/tddft_tpssh.out",
        full_width=True,
    )
    file_text
    return (file_text,)


@app.cell
def _(Path, file_text, mo):
    file = Path(file_text.value)

    if not file.exists():
        mo.md("File not found!")
    return (file,)


@app.cell
def _(mo):
    fwhm_number = mo.ui.slider(
        label="FWHM",
        start=0,
        stop=5000,
        value=2000,
        step=100,
        show_value=True,
        debounce=True,
    )
    fwhm_number
    return (fwhm_number,)


@app.cell
def _(OrcaOutput, file_text, mo):
    data = None

    try:
        data = OrcaOutput(file_text.value)
    except FileNotFoundError as e:
        print(e)

    mo.stop(data is None)
    return (data,)


@app.cell
def _(create_simulated_spectrum_chart, data, fwhm_number, mo):
    _chart = create_simulated_spectrum_chart(
        data.absorption_spectrum, fwhm=fwhm_number.value
    )

    c = mo.ui.altair_chart(_chart)
    c
    return (c,)


@app.cell
def _(c, data):
    selection = c.apply_selection(data.absorption_spectrum)
    return (selection,)


@app.cell
def _(cotwo, data, file_text):
    tda = data.tamm_dancoff
    n_roots = data.n_roots

    structure = cotwo.Molecule.from_file(file_text.value)
    return (structure,)


@app.cell
def _(data, file, mo, pl, selection, structure):
    mo.stop(len(selection) > 1)

    gbw_file = file.with_suffix(".gbw")

    with mo.status.spinner(title="Rendering difference density..") as _spinner:
        _to_state = selection["to_state"].item()
        _state_vec = data.get_state_vector(_to_state)
        _diffdens = structure.create_difference_density(
            gbw_file, state_vector=_state_vec
        )
        _fig = structure.create_fig_with_isosurface(
            _diffdens, isovalue=0.0025, colors=("#CCBE00", "#CC0022")
        )

    root = mo.ui.table(
        data.excited_states.filter(pl.col("state_id") == _to_state)
        .select(
            pl.col("from_orb"),
            pl.col("to_orb"),
            pl.col("weight").round(2),
        )
        .sort(by="weight", descending=True),
        selection="single",
    )

    mo.md(
        f"State {_to_state} (State Vector: {_state_vec})\n{mo.hstack([mo.ui.plotly(_fig), root])}"
    )
    return gbw_file, root


@app.cell
def _(gbw_file, mo, root, structure):
    mo.stop(root.value.is_empty())

    with mo.status.spinner(title="Rendering molecular orbitals..") as _spinner:
        _from_orb = root.value["from_orb"].item()
        _to_orb = root.value["to_orb"].item()

        _donor = structure.create_molecular_orbital(gbw_file, _from_orb)
        _acceptor = structure.create_molecular_orbital(gbw_file, _to_orb)

        _donor_fig = mo.ui.plotly(
            structure.create_fig_with_isosurface(_donor, isovalue=0.05)
        )
        _acceptor_fig = mo.ui.plotly(
            structure.create_fig_with_isosurface(_acceptor, isovalue=0.05)
        )

    mo.hstack(
        [
            mo.md(f"Donor Orbital ({_from_orb}) {_donor_fig}"),
            mo.md(f"Acceptor Orbital ({_to_orb}) {_acceptor_fig}"),
        ]
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
