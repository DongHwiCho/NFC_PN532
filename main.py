import binascii
import datetime
import platform
import os

# Import pn532picustom module
from pn532picustom.nfc import pn532


class NfcController:
    '''
    input : COM or SPI / 통신방식 선택
    process : 생성자, nfc 모듈 사용을 위한 설정 및 초기화 진행
    output : None
    '''

    def __init__(self, mode="COM"):
        # 비 리눅스 환경 테스트 위해 동적 import
        if (mode == "SPI"):
            from pn532picustom.interfaces.pn532spi import Pn532Spi
            self.PN532_PORT = Pn532Spi(Pn532Spi.SS0_GPIO8)
        elif (mode == "COM"):
            from pn532picustom.interfaces.pn532hsu import Pn532Hsu
            if platform.system() == "Windows":  # Windows
                self.PN532_PORT = Pn532Hsu("COM4")
            elif platform.system() == "Darwin":  # macos
                self.PN532_PORT = Pn532Hsu("/dev/ttyUSB0")
            else:  # Linux
                try:
                    if os.uname().nodename == "raspberrypi":  # Raspberry Pi
                        self.PN532_PORT = Pn532Hsu("/dev/serial0")
                    else:  # Other
                        self.PN532_PORT = Pn532Hsu("/dev/ttyUSB0")
                except:  # os.uname()이 없는 시스템일 경우 지정
                    self.PN532_PORT = Pn532Hsu("/dev/ttyUSB0")
        else:
            raise RuntimeError("Please choose mode COM/SPI")
        self.nfc = pn532.Pn532(self.PN532_PORT)

    '''
    input : timeout
    process : Felica 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''
    def nfc_start(self):
        self.nfc.begin()
        self.nfc.setPassiveActivationRetries(0xFF)
        self.nfc.SAMConfig()

    '''
    input : timeout
    process : Felica 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''
    def find_felica(self, timeout):
        self.nfc_start()
        systemCode = 0xFFFF  # Setting System Code
        requestCode = 0x01  # System Code request

        ret, idm, _, _ = self.nfc.felica_Polling(systemCode, requestCode, timeout=timeout)
        self.nfc.close()

        if ret != 1:  # Timeout
            return None
        else:  # Read Success
            return binascii.hexlify(idm)

    '''
    input : timeout
    process : ISO14443A 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''

    def find_iso14443a(self, timeout):
        self.nfc_start()
        # Read ISO14443A Card
        success, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS, timeout=timeout)
        self.nfc.close()

        if success:  # Read Success
            return binascii.hexlify(uid)
        else:  # Timeout
            return None

    '''
    input : timeout=1000 (detect 한번의 로직 timeout)
    process : 카드 인식을 기다리다가 카드를 읽으면 해당 카드의 uid를 반환한다. 인식되지 않으면 None을 반환한다.
    output : string (카드의 uid)
    '''

    def detect(self, timeout=1000):
        try:
            uid = self.find_felica(timeout / 2)
            if uid is not None:
                return uid
            else:
                return self.find_iso14443a(timeout / 2)
        except:
            return None


class DummyNfcController:
    def __init__(self, detect_interval=10, mode="COM"):
        self.__mode = mode
        self.__interval = detect_interval
        self.__last_detect = datetime.datetime.now()
        self.__return_data = False

    '''
    input : timeout=1000 (detect 한번의 로직 timeout)
    process : 1 Cycle : None 반환 -> interval 초 후 id 반환 (Cycle interval 초 마다 반복)
    output : string (카드의 uid)
    '''

    def detect(self, timeout=1000):
        result = None
        if self.__return_data:
            result = 'a12345678'
        sec_diff = ((datetime.datetime.now() - self.__last_detect).total_seconds())
        if sec_diff > self.__interval:
            self.__last_detect = datetime.datetime.now()
            self.__return_data = not self.__return_data
        return result


# test
if __name__ == '__main__':
    nfc = NfcController()
    while True:
        print(nfc.detect())
