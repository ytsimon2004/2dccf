from argclz.commands import parse_command_args

from .main_view import ViewSliceOptions

parse_command_args(
    usage='python -m rscvp.spatial [CMD] ...',
    description='plot and store spatial-related parameters',
    parsers=dict(
        view=ViewSliceOptions
    )
)
