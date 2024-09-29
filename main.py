import time
import binascii

# Import pn532pi module
from pn532pi.nfc import pn532
from pn532pi.interfaces import pn532hsu

# Generate and Setting PN532 NFC Module and SPI PORT
PN532_HSU = pn532hsu.Pn532Hsu(3)
nfc = pn532.Pn532(PN532_HSU)

# setup Method
def setup():
  print("NTAG21x R/W")
  print("-------Looking for pn532--------")

  nfc.begin()

  versiondata = nfc.getFirmwareVersion()
  if not versiondata:
    print("Didn't find PN53x board")
    raise RuntimeError("Didn't find PN53x board")  # halt

  # Got ok data, print it out!
  print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                              (versiondata >> 8) & 0xFF))

  # Set the max number of retry attempts to read from a card
  # This prevents us from waiting forever for a card, which is
  # the default behaviour of the pn532.
  nfc.setPassiveActivationRetries(0xFF)
  nfc.SAMConfig()


# Read Felica Method
def find_felica():
    systemCode = 0xFFFF # Setting System Code
    requestCode = 0x01  # System Code request

    # Wait for an FeliCa type cards.
    # When one is found, some basic information such as IDm, PMm, and System Code are retrieved.
    print("Waiting for an FeliCa card...  ")
    # Read Felica NFC Card
    ret, idm, pwm, systemCodeResponse = nfc.felica_Polling(systemCode, requestCode, timeout=1000)

    # Timeout
    if ret != 1:
        print("Could not find a Felica card")
        time.sleep(0.5)
        return

    # Read Success
    print("Found a Felica card!")
    print(f"UID : {binascii.hexlify(idm)}")
    time.sleep(3)


# Read ISO14443A Method
def find_iso14443a():
    print("Waiting for an ISO14443A card...  ")
    # Read ISO14443A Card
    success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS, timeout=1000)

    # Read Success
    if success:
        print("Found a ISO14443A card!")
        print(f"UID : {binascii.hexlify(uid)}")
        time.sleep(3)
    else :
        # Timeout
        print("Could not find a ISO14443A card")
        time.sleep(0.5)


# Read ISO15693 Method but didn't work...
def find_other():
    print("Waiting for an Other card...  ")
    # Test for ISO15693 Card but can not read.....
    success, uid = nfc.readPassiveTargetID(pn532.PN532_FELICA_424KBPS, timeout=1000)

    # Read Success
    if success:
        print("Found a Other card!")
        print(f"UID : {binascii.hexlify(uid)}")
        time.sleep(3)
    else:
        # Timeour
        print("Could not find a Other card")
        time.sleep(0.5)


# Infinite loop
def loop():
    # Check correct type of NFC
    find_felica()
    find_iso14443a()
    find_other()


# Main
if __name__ == '__main__':
    setup()
    while True:
        loop()