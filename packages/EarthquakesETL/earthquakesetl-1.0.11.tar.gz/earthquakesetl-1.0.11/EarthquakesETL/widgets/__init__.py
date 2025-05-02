import sysconfig

DESCRIPTION = "Earth Quake Prediction tools for Orange."

BACKGROUND = "#ffacc5"

ICON = "icons/EarthquakesETL.svg"

# Location of widget help files.
WIDGET_HELP_PATH = (
    # Development documentation
    # You need to build help pages manually using
    # make htmlhelp
    # inside doc folder
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),

    # Documentation included in wheel
    # Correct DATA_FILES entry is needed in setup.py and documentation has to be built
    # before the wheel is created.
    ("{}/help/orange3-example/index.html".format(sysconfig.get_path("data")), None)
)