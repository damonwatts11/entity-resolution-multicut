"""Streamlit demonstration application (Level F, project document, spec.md 5.3).

The application imports the package and contains no resolution logic of its own.
Controls: theta, rho, B, seed, and n capped at 5000. One view per pipeline step
and a comparison view (transitive closure versus certified decomposition).

This is a scaffold. Run with: `make app` (requires the 'app' extra:
`pip install -e ".[app]"`).
"""

from __future__ import annotations

import streamlit as st

import ermc


def main() -> None:
    st.set_page_config(page_title="Certified decomposition", layout="wide")
    st.title("Entity resolution by certified decomposition")
    st.caption(f"ermc {ermc.__version__} -- demonstration scaffold")

    with st.sidebar:
        st.header("Controls")
        st.slider("theta (corruption)", 0.0, 0.3, 0.1, 0.05)
        st.slider("rho (confusable density)", 0.0, 0.4, 0.1, 0.05)
        st.select_slider("B (kernel cap)", options=[25, 50, 100, 200, 400, 800], value=100)
        st.number_input("seed", min_value=0, value=0, step=1)
        st.number_input("n (records, capped)", min_value=10, max_value=5000, value=1000, step=10)

    st.info(
        "Scaffold: the pipeline is not implemented yet. When it is, this page "
        "shows one view per pipeline step and a side-by-side comparison with "
        "transitive closure, including U, L, Delta and gamma."
    )


if __name__ == "__main__":
    main()
