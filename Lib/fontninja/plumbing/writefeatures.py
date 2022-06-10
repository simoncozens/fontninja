class WriteFeatures:
    """Write an extended feature file for a UFO (kerning, anchors, etc.)"""

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument("input", metavar="INPUT", help="Input UFO file")
        parser.add_argument("output", metavar="OUTPUT", help="Output FEA file")

    @classmethod
    def run(cls, args):
        from ufo2ft.featureCompiler import FeatureCompiler
        import ufoLib2

        ufo = ufoLib2.Font.open(args.input)
        fc = FeatureCompiler(ufo)
        fc.setupFeatures()
        fc.writeFeatures(open(args.output, "w"))
