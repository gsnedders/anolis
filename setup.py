from distutils.core import setup

setup(name = "specGen",
	license="""MIT""",
	version = "1.0b1.1-dev",
	author = "Geoffrey Sneddon",
	author_email = "geoffers@gmail.com",
	packages = ["specGen", "specGen/processes"],
	scripts = ["spec-gen"],
	)
