from __future__ import print_function
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.util import toHexString
import time


class TracerAndSELECTInterpreter(CardConnectionObserver):
    """This observer will interprer SELECT and GET RESPONSE bytes
        and replace them with a human readable string."""

    def update(self, cardconnection, ccevent):

        if 'connect' == ccevent.type:
            print('connecting to ' + cardconnection.getReader())

        elif 'disconnect' == ccevent.type:
            print('disconnecting from ' + cardconnection.getReader())

        elif 'command' == ccevent.type:
            str = toHexString(ccevent.args[0])
            str = str.replace("A0 A4 00 00 07", "SELECT")
            str = str.replace("A0 C0 00 00", "GET RESPONSE")
            print('>', str)

        elif 'response' == ccevent.type:
            if [] == ccevent.args[0]:
                print('<  []', "%-2X %-2X" % tuple(ccevent.args[-2:]))
            else:
                print('<',
                      toHexString(ccevent.args[0]),
                      "%-2X %-2X" % tuple(ccevent.args[-2:]))


# define the APDUS used in this script
GET_RESPONSE = [0XA0, 0XC0, 00, 00]
SELECT = [0x00, 0xA4, 0x04, 0x00, 0x07]
DF_TELECOM = [0x04, 0x78, 0x52, 0xEA, 0xB0, 0x43, 0x80] # EXAMPLE AID

# we request any type and wait for 10s for card insertion

while(1):
    try:
        cardtype = AnyCardType()
        print ("EN ATTENTE:")
        cardrequest = CardRequest(timeout=100, cardType=cardtype)
        cardservice = cardrequest.waitforcard()

        # create an instance of our observer and attach to the connection
        observer = TracerAndSELECTInterpreter()
        cardservice.connection.addObserver(observer)


        # connect and send APDUs
        # the observer will trace on the console

        cardservice.connection.connect()

        apdu = SELECT + DF_TELECOM
        response, sw1, sw2 = cardservice.connection.transmit(apdu)
        print ("IT SELECTED")
        continue

        if sw1 == 0x90:
            apdu = GET_RESPONSE + [sw2]
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
        else:
            print('no CARD')

        import sys
        if 'win32' == sys.platform:
            print('press Enter to continue')
            sys.stdin.read(1)
    except:
        pass
