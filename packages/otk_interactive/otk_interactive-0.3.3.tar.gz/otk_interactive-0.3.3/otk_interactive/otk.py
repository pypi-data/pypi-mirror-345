import plotly.express as px
from optical_toolkit.visualize.embeddings import get_embeddings


def interactive_embeddings(X, y, dims=2, embedding_type="tsne"):
    """
    Generate 2D or 3D interactive scatter plots from embeddings.

    Args:
    - X: Features to embed.
    - y: Labels corresponding to X.
    - dims: Number of dimensions for the embedding (2 or 3).
    - embedding_type: Type of embedding to use (e.g., 'tsne', 'umap').

    Returns:
    - fig: Plotly Figure object.
    """
    embeddings = get_embeddings(
        X, y, embedding_dims=dims, embedding_type=embedding_type, return_plot=False
    )
    df = {f"dim{i+1}": embeddings[:, i] for i in range(dims)}
    df["label"] = y

    if dims == 2:
        fig = px.scatter(
            df,
            x="dim1",
            y="dim2",
            color="label",
            title=f"{embedding_type.upper()} Embedding (2D)",
            labels={"color": "Label"},
        )
    elif dims == 3:
        fig = px.scatter_3d(
            df,
            x="dim1",
            y="dim2",
            z="dim3",
            color="label",
            title=f"{embedding_type.upper()} Embedding (3D)",
            labels={"color": "Label"},
        )
    else:
        raise ValueError("Only 2D and 3D visualizations are supported (dims=2 or 3).")

    fig.update_traces(marker=dict(size=5, opacity=0.7))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))

    return fig
