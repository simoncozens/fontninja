class Cu2Qu:
    """Convert curves from cubic to quadratic"""

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument(
            "--reverse-direction",
            help="Reverse curve direction",
            type=bool,
            default=False,
        )
        parser.add_argument(
            "--remember-curve-type", help="Store the curve type in a private lib key"
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument("--max-err", help="Maximum error in font units")
        group.add_argument(
            "--max-err-em", help="Maximum error in fractions of the em square"
        )

        parser.add_argument("input", metavar="INPUT", help="Input UFO file")
        parser.add_argument("output", metavar="OUTPUT", help="Output UFO file")

    @classmethod
    def run(cls, args):
        from cu2qu.ufo import font_to_quadratic
        import ufoLib2

        ufo = ufoLib2.Font.open(args.input)
        font_to_quadratic(
            ufo,
            max_err_em=args.max_err_em,
            max_err=args.max_err,
            reverse_direction=args.reverse_direction,
            remember_curve_type=args.remember_curve_type,
        )
        ufo.save(args.output)
