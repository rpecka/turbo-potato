import configparser


DEFAULT_TARGET_SIZE = 8  # Discord free tier maximum
DEFAULT_MAX_FPS = None
DEFAULT_MAX_RESOLUTION = None


SECTION_DEFAULTS = "defaults"
KEY_DEFAULT_TARGET_SIZE = "targetSize"
KEY_DEFAULT_MAX_FPS = "maxFPS"
KEY_DEFAULT_RESOLUTION = "maxResolution"


class Config:
    def __init__(self, path):
        config = configparser.ConfigParser()
        config.read(path)

        self.default_target_size = config.getfloat(SECTION_DEFAULTS, KEY_DEFAULT_TARGET_SIZE, fallback=DEFAULT_TARGET_SIZE)
        self.default_max_fps = config.getint(SECTION_DEFAULTS, KEY_DEFAULT_MAX_FPS, fallback=DEFAULT_MAX_FPS)
        self.default_max_resolution = config.get(SECTION_DEFAULTS, KEY_DEFAULT_RESOLUTION, fallback=DEFAULT_MAX_RESOLUTION)
