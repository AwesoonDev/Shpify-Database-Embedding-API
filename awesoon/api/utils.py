from flask_restx import inputs


def add_pagination_params(parser):
    parser.add_argument(
        "limit",
        type=inputs.positive,
        required=False,
        location="values",
        default=100
    )
    parser.add_argument(
        "offset",
        type=int,
        required=False,
        location="values",
        default=0
    )
    return parser

