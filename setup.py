from distutils.core import setup

setup(name = "specGen",
	license="""MIT""",
	version = "0.0",
	author = "Geoffrey Sneddon",
	author_email = "geoffers@gmail.com",
	packages = ["specGen"],
	package_dir = {"": "src"},
	scripts = ["spec-gen"],
	)
