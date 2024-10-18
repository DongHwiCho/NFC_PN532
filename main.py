import time
import binascii

# Import pn532pi module
from pn532pi import pn532
from pn532pi import Pn532Spi, Pn532Hsu

class NfcController:
    '''
    input : COM or SPI / 통신방식 선택
    process : 생성자, nfc 모듈 사용을 위한 설정 및 초기화 진행
    output : None
    '''
    def __init__(self, mode="COM"):
        if(mode == "SPI"):
            self.PN532_PORT = Pn532Spi(Pn532Spi.SS0_GPIO8)
        elif(mode == "COM"):
            self.PN532_PORT = Pn532Hsu(0)
        self.nfc = pn532.Pn532(self.PN532_PORT)

        self.nfc.begin()

        versiondata = nfc.getFirmwareVersion()
        if not versiondata:
            print("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")  # halt

        # Set the max number of retry attempts to read from a card
        # This prevents us from waiting forever for a card, which is
        # the default behaviour of the pn532.
        self.nfc.setPassiveActivationRetries(0xFF)
        self.nfc.SAMConfig()

    '''
    input : timeout
    process : Felica 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''
    def find_felica(self, timeout):
        systemCode = 0xFFFF # Setting System Code
        requestCode = 0x01  # System Code request

        ret, idm, _, _ = self.nfc.felica_Polling(systemCode, requestCode, timeout=timeout)

        if ret != 1: # Timeout
            return None
        else: # Read Success
            return binascii.hexlify(idm)

    '''
    input : timeout
    process : ISO14443A 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''
    def find_iso14443a(self, timeout):
        # Read ISO14443A Card
        success, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS, timeout=timeout)

        if success: # Read Success
            return binascii.hexlify(uid)
        else : # Timeout
            return None

    '''
    input : timeout=1000
    process : 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''
    def detect(self, timeout=1000):
        uid = self.find_felica(timeout)
        if uid is not None:
            return uid
        else:
            return self.find_iso14443a(timeout)


# test
if __name__ == '__main__':
    nfc = NfcController()
    while True:
        print(nfc.detect())