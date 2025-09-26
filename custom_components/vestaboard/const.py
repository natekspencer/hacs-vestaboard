"""Constants for the Vestaboard integration."""

from typing import Final

DOMAIN: Final = "vestaboard"

ALIGN_CENTER: Final = "center"
ALIGN_LEFT: Final = "left"
ALIGN_RIGHT: Final = "right"
ALIGNS: Final = [ALIGN_CENTER, ALIGN_LEFT, ALIGN_RIGHT]

CONF_ALIGN: Final = "align"
CONF_DECORATOR: Final = "decorator"
CONF_ENABLEMENT_TOKEN: Final = "enablement_token"
CONF_JUSTIFY: Final = "justify"
CONF_MESSAGE: Final = "message"
CONF_MODEL: Final = "model"
CONF_QUIET_END: Final = "quiet_end"
CONF_QUIET_START: Final = "quiet_start"
CONF_VALIGN: Final = "valign"
CONF_VBML: Final = "vbml"

DATA_HASS_CONFIG: Final = "hass_config"

DECORATOR_MUSIC: Final = "music"
DECORATORS: Final = [DECORATOR_MUSIC]

MODEL_BLACK: Final = "black"
MODEL_WHITE: Final = "white"

SERVICE_MESSAGE: Final = "message"
VBML_URL: Final = "https://vbml.vestaboard.com/compose"

VALIGN_BOTTOM: Final = "bottom"
VALIGN_MIDDLE: Final = "middle"
VALIGN_TOP: Final = "top"
VALIGNS: Final = [VALIGN_BOTTOM, VALIGN_MIDDLE, VALIGN_TOP]
