import time
import binascii

# Import pn532pi module
from pn532pi import pn532
from pn532pi import Pn532Spi

PN532_SPI = Pn532Spi(0)
nfc = pn532.Pn532(PN532_SPI)


# setup Method
def setup():
  nfc.begin()

  versiondata = nfc.getFirmwareVersion()
  if not versiondata:
    print("Didn't find PN53x board")
    raise RuntimeError("Didn't find PN53x board")  # halt

  # Set the max number of retry attempts to read from a card
  # This prevents us from waiting forever for a card, which is
  # the default behaviour of the pn532.
  nfc.setPassiveActivationRetries(0xFF)
  nfc.SAMConfig()


'''
input : timeout
process : Felica 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
output : string (카드의 uid)
'''
def find_felica(timeout):
    systemCode = 0xFFFF # Setting System Code
    requestCode = 0x01  # System Code request

    ret, idm, _, _ = nfc.felica_Polling(systemCode, requestCode, timeout=timeout)

    if ret != 1: # Timeout
        return None
    else: # Read Success
        return binascii.hexlify(idm)


'''
input : timeout
process : ISO14443A 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
output : string (카드의 uid)
'''
def find_iso14443a(timeout):
    # Read ISO14443A Card
    success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS, timeout=timeout)

    if success: # Read Success
        return binascii.hexlify(uid)
    else : # Timeout
        return None


'''
input : timeout=1000
process : 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
output : string (카드의 uid)
'''
def detect(timeout=1000):
    uid = None
    setup()
    uid = find_felica(timeout)
    if uid is not None:
        return uid
    else:
        return find_iso14443a(timeout)


# test
if __name__ == '__main__':
    while True:
        print(detect())