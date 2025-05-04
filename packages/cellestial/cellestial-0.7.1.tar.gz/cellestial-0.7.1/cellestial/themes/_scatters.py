from lets_plot import (
    element_text,
    ggsize,
    scale_color_viridis,
    theme,
    theme_classic,
)

_THEME_DIMENSION = (
    theme_classic()
    + theme(
        # customize all text
        text=element_text(color="#1f1f1f", family="Arial"),
        # customize all titles (includes legend)
        title=element_text(color="#1f1f1f", family="Arial"),
        # customize axis titles (labels)
        axis_title=element_text(color="#3f3f3f", family="Arial"),
        # customize legend text
        legend_text=element_text(color="#1f1f1f", size=11, face="plain"),
        # customize legend columns
    )
    + ggsize(500, 400)
)

_THEME_SCATTER = (
    theme_classic()
    + theme(
        # customize all text
        text=element_text(color="#1f1f1f", family="Arial"),
        # customize all titles (includes legend)
        title=element_text(color="#1f1f1f", family="Arial"),
        # customize axis titles (labels)
        axis_title=element_text(color="#3f3f3f", family="Arial"),
        # customize legend text
        legend_text=element_text(color="#1f1f1f", size=11, face="plain"),
        # customize legend columns
    )
    + ggsize(500, 400)
    + scale_color_viridis()
)
