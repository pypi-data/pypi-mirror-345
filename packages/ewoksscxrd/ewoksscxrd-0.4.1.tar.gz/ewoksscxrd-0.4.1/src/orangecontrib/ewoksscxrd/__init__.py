import sysconfig

NAME = "Ewoks Examples"

DESCRIPTION = "Ewoks Examples"

LONG_DESCRIPTION = "Ewoks Examples"

ICON = "icons/category.svg"

BACKGROUND = "light-blue"

WIDGET_HELP_PATH = (
    # Development documentation (make htmlhelp in ./doc)
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),
    # Documentation included in wheel
    ("{}/help/ewoksscxrd/index.html".format(sysconfig.get_path("data")), None),
    # Online documentation url
    ("https://ewoksscxrd.readthedocs.io", ""),
)
