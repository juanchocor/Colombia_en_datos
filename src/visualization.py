"""Funciones base para construir visualizaciones."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str = ""):
    """Crea una grafica de barras sencilla y devuelve la figura."""
    fig, ax = plt.subplots()
    ax.bar(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig
