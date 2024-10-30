try:
    from .interfaces.pn532spi import Pn532Spi
    from .interfaces.pn532hsu import Pn532Hsu
except:        # Allow unit tests to run without importing interfaces
    Pn532Hsu = None
    Pn532Spi = None


from .nfc.pn532_log import DEBUG
from .nfc import pn532
from .nfc.pn532 import Pn532
from .nfc.llcp import Llcp
from .nfc.snep import Snep
from .nfc.emulatetag import EmulateTag
