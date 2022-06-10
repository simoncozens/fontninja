from .cu2qu import Cu2Qu
from .cu2qu_interpolatable import Cu2QuInterpolatable
from .writefeatures import WriteFeatures
from .compilefeatures import CompileFeatures
from .decomposemixed import DecomposeMixed
from .ufo2ttf import Ufo2Ttf

commands = {
	"compile-features": CompileFeatures,
	"writefeatures": WriteFeatures,
	"decompose-mixed": DecomposeMixed,
	"cu2qu": Cu2Qu,
	"cu2qu-interpolatable": Cu2QuInterpolatable,
	"ufo2ttf": Ufo2Ttf
}

def run(parser):
	parser.description = "Font builder (low-level)"
	subparsers = parser.add_subparsers()
	for command, impl in commands.items():
			subparser = subparsers.add_parser(command)
			impl.setup_parser(subparser)
			subparser.set_defaults(func=impl.run)
	args = parser.parse_args()
	args.func(args)

def setup_ninja_rules(writer):
	writer.comment("Rules\n")
	call_self = f"python3 -m fontninja --plumbing"
	for command, impl in commands.items():
		writer.comment(impl.__doc__)
		if hasattr(impl, "ninja_args"):
			writer.rule(command, f"{call_self} {command} {impl.ninja_args}")
		else:
			writer.rule(command, f"{call_self} {command} $args $in $out")
		writer.newline()
