from src import nfc, utils
import mizipCalcKeys
from smartcard.util import toHexString
from smartcard.ATR import ATR
import customtkinter


# stuffs
vUID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
KEYS = []
BLOCCHI = []

auth_A = []
load_auth_A = []

auth_B = []
load_auth_B = []


def getUID():
    fUID = ''
    UID = reader.connection.transmit(vUID)
    UID = utils.int_list_to_hexadecimal_list(UID[0])
    for i in UID:
        fUID = fUID + i[2:4].upper()
    return fUID


def autenticazioni():
    authentication_A()
    authentication_B()


def authentication_A():
    KA = []
    count = 0
    block = 0
    for key in KEYS[0]:
        if count == 0:
            block = 0x00
        elif count == 1:
            block = 0x04
        elif count == 2:
            block = 0x08
        elif count == 3:
            block = 0x0C
        else:
            block = 0x10
        res = [key[i:i+2] for i in range(0, len(key), 2)]
        for i in res:
            i = int(i, 16)
            KA.append(i)
        load_auth_A.append([KA[0], KA[1], KA[2], KA[3], KA[4], KA[5]])
        auth_A.append(block)
        KA = []
        count += 1


def authentication_B():
    KB = []
    count = 0
    block = 0
    for key in KEYS[1]:
        if count == 0:
            block = 0x00
        elif count == 1:
            block = 0x04
        elif count == 2:
            block = 0x08
        elif count == 3:
            block = 0x0C
        else:
            block = 0x10
        res = [key[i:i+2] for i in range(0, len(key), 2)]
        for i in res:
            i = int(i, 16)
            KB.append(i)
        load_auth_B.append([KB[0], KB[1], KB[2], KB[3], KB[4], KB[5]])
        auth_B.append(block)
        KB = []
        count += 1
 

def readCredit():
    reader.load_authentication_data(0x00, load_auth_A[2])
    reader.authentication(auth_A[2],0x60,0x00)
    reader.load_authentication_data(0x01, load_auth_B[2])
    reader.authentication(auth_B[2],0x61,0x01)

    creditoHEX = reader.read_binary_blocks(0x08, 0x7)
    checkCreditPosition = reader.read_binary_blocks(0x0A, 0x1)
    if str(hex(checkCreditPosition[0])) == '0xaa':
        b1 = str(hex(creditoHEX[1]))
        b1 = b1.replace('0x', '')
        while len(b1) < 2:
            b1 = '0' + b1
        b2 = str(hex(creditoHEX[2]))
        b2 = b2.replace('0x', '')
        while len(b2) < 2:
            b2 = '0' + b2
    else:
        b1 = str(hex(creditoHEX[4]))
        b1 = b1.replace('0x', '')
        while len(b1) < 2:
            b1 = '0' + b1
        b2 = str(hex(creditoHEX[5]))
        b2 = b2.replace('0x', '')
        while len(b2) < 2:
            b2 = '0' + b2

    res = (b2) + (b1)
    res = int(res, 16)
    res = str(res)

    if len(res) > 2:
        res = res[0:-2] + ',' + res[-2:]
    elif len(res) == 1:
        res = '0,0' + res
    else:
        res = '0,' + res
    res = res + ' €'

    return res



# reader init
reader = nfc.Reader()

# keys calc
KEYS = mizipCalcKeys.calc(getUID())

# authentications
autenticazioni()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("MIZIP Charger")
        self.minsize(400, 300)
        self.resizable(False, False)
        
        self.label3 = customtkinter.CTkLabel(master=self, text="")
        self.label3.pack(padx=20, pady=5)

        self.label4 = customtkinter.CTkLabel(master=self, text="UID").place(x=35, y=0)

        self.entryUID = customtkinter.CTkEntry(master=self, placeholder_text=getUID(), width=75).place(x=10, y=30)

        self.entry = customtkinter.CTkEntry(master=self, placeholder_text="Inserisci Credito")
        self.entry.pack(padx=20, pady=10)

        self.button = customtkinter.CTkButton(master=self, text="SCRIVI", command=self.scriviCredito)
        self.button.pack(padx=20, pady=30)

        self.label2 = customtkinter.CTkLabel(master=self, text="credito attuale")
        self.label2.pack(padx=20, pady=0)

        self.entry1 = customtkinter.CTkEntry(master=self, placeholder_text=readCredit())
        self.entry1.pack(padx=20, pady=0)
        
        self.label = customtkinter.CTkLabel(master=self, text="")
        self.label.pack(padx=20, pady=10)


    def write_16(self,reader, position, number, data):
        reader.update_binary_blocks(position, number, data)
    

    def write(self, reader, position, number, data):
        while number >= 7:
            self.write_16(reader, position, 16, data)
            number -= 7
            position += 1
    

    def convert(self, val):
        val = str(hex(val))
        val = val.replace('0x', '')
        val = int(val, 16)
        return val

    
    def chksum(self, v1, v2):
        return v1 ^ v2


    def scriviCredito(self):
        creditHex = []

        self.label.configure(text="")

        c1 = self.entry.get()

        c1 = c1.strip().replace(".","").replace(",","")

        if len(c1) == 0:
            self.label.configure(text="Nessun credito inserito")
            return 1

        try:
            c1 = int(c1)
        except:
            self.label.configure(text="Valore inserito non valido")
            return 1
            
        if c1 > 65535:
            self.label.configure(text="Il credito massimo impostabile è di 655,35 Euro")
            return 1
        else:
            c2 = hex(c1)
            
            while len(c2) < 6:
                c2 = '0x0' + c2[2:] 

            creditHex.append('0x' + c2[4:])
            creditHex.append(c2[0:4])
            
            v1 = creditHex[0]
            v2 = creditHex[1]
            v1 = v1.replace('0x', '')
            v2 = v2.replace('0x', '')
            v1 = int(v1, 16)
            v2 = int(v2, 16)

            reader.load_authentication_data(0x00, load_auth_A[2])
            reader.load_authentication_data(0x01, load_auth_B[2])
            reader.authentication(auth_A[2],0x60,0x00)
            reader.authentication(auth_B[2],0x61,0x01)

            checkCreditPosition = reader.read_binary_blocks(0x0A, 0x1)
            if str(hex(checkCreditPosition[0])) == '0xaa':
                creditoPresente = reader.read_binary_blocks(0x08, 0x7)
                self.write(reader, 0x08, 0x07, [self.convert(creditoPresente[0]), v1, v2, self.chksum(v1, v2), self.convert(creditoPresente[4]), self.convert(creditoPresente[5]), self.convert(creditoPresente[6])])
            else:
                creditoPresente = reader.read_binary_blocks(0x08, 0x7)
                self.write(reader, 0x08, 0x07, [self.convert(creditoPresente[0]), self.convert(creditoPresente[1]), self.convert(creditoPresente[2]), self.convert(creditoPresente[3]), v1, v2, self.chksum(v1, v2)])

            
            self.entry1.delete(0, 1000)
            self.entry1.insert(0, readCredit())


if __name__ == "__main__":
    app = App()
    app.mainloop()