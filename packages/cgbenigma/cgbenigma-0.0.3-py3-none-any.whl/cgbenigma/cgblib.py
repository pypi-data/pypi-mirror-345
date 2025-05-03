class Enigma:
    """Represents an Enigma machine.
    Initializes an Enigma machine with these arguments:
    - ref: reflector;
    - r1, r2, r3: rotors;
    - key: initial state of rotors;
    - plus: plugboard settings.
    """

    def __init__(self, ref, r1, r2, r3, key="AAA", plugs="", ring="AAA", notchs="", debug=False):
        """Initialization of the Enigma machine."""
        self.reflector = ref
        self.rotor1 = r1
        self.rotor2 = r2
        self.rotor3 = r3

        self.rotor1.state = key[0]
        self.rotor2.state = key[1]
        self.rotor3.state = key[2]
        self.rotor1.ring = ring[0]
        self.rotor2.ring = ring[1]
        self.rotor3.ring = ring[2]
        if len(notchs) >= 3:
            self.rotor1.notchs = notchs[0]
            self.rotor2.notchs = notchs[1]
            self.rotor3.notchs = notchs[2]
        self.reflector.state = "A"
        self.rotor1.debug = debug
        self.rotor2.debug = debug
        self.rotor3.debug = debug
        self.reflector.debug = debug
        self.debug = debug

        plugboard_settings = [(elem[0], elem[1]) for elem in plugs.split()]

        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        alpha_out = [" "] * 26
        for i in range(len(alpha)):
            alpha_out[i] = alpha[i]
        for k, v in plugboard_settings:
            alpha_out[ord(k) - ord("A")] = v
            alpha_out[ord(v) - ord("A")] = k

        try:
            self.transtab = str.maketrans(alpha, "".join(alpha_out))
        except:
            # Python 2
            from string import maketrans

            self.transtab = maketrans(alpha, "".join(alpha_out))

    def encipher(self, plaintext_in):
        """Encrypt 'plaintext_in'."""
        ciphertext = ""
        plaintext_in_upper = plaintext_in.upper()
        plaintext = plaintext_in_upper.translate(self.transtab)
        for c in plaintext:

            # ignore non alphabetic char
            if not c.isalpha():
                ciphertext += c
            else:
                t = self.rotor1.encipher_right(c)
                t = self.rotor2.encipher_right(t)
                t = self.rotor3.encipher_right(t)
                t = self.reflector.encipher(t)
                t = self.rotor3.encipher_left(t)
                t = self.rotor2.encipher_left(t)
                t = self.rotor1.encipher_left(t)
                ciphertext += t

            if self.rotor1.is_in_turnover_pos():
                if self.rotor2.is_in_turnover_pos():
                    self.rotor3.notch()
                self.rotor2.notch()
            self.rotor1.notch()
            if self.debug:
                print('[states] : ', self.rotor1.state, self.rotor2.state, self.rotor3.state, sep='');

        res = ciphertext.translate(self.transtab)

        fres = ""
        for idx, char in enumerate(res):
            if plaintext_in[idx].islower():
                fres += char.lower()
            else:
                fres += char
        return fres
    
    def __str__(self):
        """Pretty display."""
        return """
        Reflector: {}
        Rotor 1: {}
        Rotor 2: {}
        Rotor 3: {}""".format(
            self.reflector, self.rotor1, self.rotor2, self.rotor3
        )

class Reflector:
    """Represents a reflector."""

    def __init__(self, wiring=None, name=None, model=None, date=None, debug=False):
        if wiring != None:
            self.wiring = wiring
        else:
            self.wiring = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.name = name
        self.model = model
        self.date = date
        self.debug = debug

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def encipher(self, key):
        shift = ord(self.state) - ord("A")
        index = (ord(key) - ord("A")) % 26  # true index
        index = (index + shift) % 26  # actual connector hit
        letter = self.wiring[index]  # rotor letter generated
        out = chr(ord("A") + (ord(letter) - ord("A") + 26 - shift) % 26)  # actual output
        if self.debug:
            print(self.name,' [---] ', self.state,': ', key,' ', out, sep='');
        # return letter
        return out

    def __eq__(self, rotor):
        return self.name == rotor.name
    
    def __str__(self):
        """Pretty display."""
        return """
        Name: {}
        Model: {}
        Date: {}
        Wiring: {}""".format(
            self.name, self.model, self.date, self.wiring
        )

class Rotor:
    """Represents a rotor."""

    def __init__(
        self,
        wiring=None,
        notchs=None,
        name=None,
        model=None,
        date=None,
        state="A",
        ring="A",
        debug=False,
    ):
        """
        Initialization of the rotor.
        """
        if wiring != None:
            self.wiring = wiring
        else:
            self.wiring = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.rwiring = ["0"] * 26
        for i in range(0, len(self.wiring)):
            self.rwiring[ord(self.wiring[i]) - ord("A")] = chr(ord("A") + i)
        if notchs != None:
            self.notchs = notchs
        else:
            self.notchs = ""
        self.name = name
        self.model = model
        self.date = date
        self.state = state
        self.ring = ring
        self.debug = debug

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == "wiring":
            self.rwiring = ["0"] * 26
            for i in range(0, len(self.wiring)):
                self.rwiring[ord(self.wiring[i]) - ord("A")] = chr(ord("A") + i)

    def encipher_right(self, key):
        shift = ord(self.state) - ord(self.ring) + 26
        index = (ord(key) - ord("A")) % 26  # true index
        index = (index + shift) % 26  # actual connector hit
        letter = self.wiring[index]  # rotor letter generated
        out = chr(ord("A") + (ord(letter) - ord("A") + 26 - shift) % 26)  # actual output
        if self.debug:
            print(self.name,' [>>>] ', self.state,': ', key,' ', out, sep='');
        return out

    def encipher_left(self, key):
        shift = ord(self.state) - ord(self.ring) + 26
        index = (ord(key) - ord("A")) % 26
        index = (index + shift) % 26
        # mapped output
        letter = self.rwiring[index]
        out = chr(ord("A") + (ord(letter) - ord("A") + 26 - shift) % 26)
        if self.debug:
            print(self.name,' [<<<] ', self.state,': ', key,' ', out, sep='');
        return out

    def notch(self, offset=1):
        r = chr((ord(self.state) + offset - ord("A")) % 26 + ord("A"))
        if self.debug:
            print(self.name,' [notch] ', self.state,' --> ', r, sep='');
        self.state = r
        notchnext = self.state in self.notchs
        return

    def is_in_turnover_pos(self):
        x = chr((ord(self.state) + 1 - ord("A")) % 26 + ord("A"))
        ret = x in self.notchs
        if self.debug:
            print(self.name,' [turnover] ? = ', ret, ', state = ', x, ', notchs = ', self.notchs, sep='');
        return ret

    def __eq__(self, rotor):
        return self.name == rotor.name

    def __str__(self):
        """
        Pretty display.
        """
        return """
        Name: {}
        Model: {}
        Date: {}
        Wiring: {}
        RWiring: {}
        State: {}""".format(
            self.name, self.model, self.date, self.wiring, ''.join(self.rwiring), self.state
        )


# 1924 Rotors
ROTOR_IC = Rotor(
    wiring="DMTWSILRUYQNKFEJCAZBPGXOHV", name="IC", model="Commercial Enigma A, B", date="1924",)
ROTOR_IIC = Rotor(wiring="HQZGPJTMOBLNCIFDYAWVEUSRKX",name="IIC",model="Commercial Enigma A, B",date="1924",)
ROTOR_IIIC = Rotor(wiring="UQNTLSZFMREHDPXKIBVYGJCWOA",name="IIIC",model="Commercial Enigma A, B",date="1924",)

# German Railway Rotors
ROTOR_GR_I = Rotor(wiring="JGDQOXUSCAMIFRVTPNEWKBLZYH",name="I",model="German Railway (Rocket)",date="7 February 1941",)
ROTOR_GR_II = Rotor(wiring="NTZPSFBOKMWRCJDIVLAEYUXHGQ",name="II",model="German Railway (Rocket)",date="7 February 1941",)
ROTOR_GR_III = Rotor(wiring="JVIUBHTCDYAKEQZPOSGXNRMWFL",name="III",model="German Railway (Rocket)",date="7 February 1941",)
ROTOR_GR_UKW = Reflector(wiring="QYHOGNECVPUZTFDJAXWMKISRBL",name="UTKW",model="German Railway (Rocket)",date="7 February 1941",)
ROTOR_GR_ETW = Rotor(wiring="QWERTZUIOASDFGHJKPYXCVBNML",name="ETW",model="German Railway (Rocket)",date="7 February 1941",)

# Swiss SONDER Rotors
ROTOR_I_SONDER = Rotor(wiring="VEOSIRZUJDQCKGWYPNXAFLTHMB",name="I-SONDER",model="Enigma Sonder",date="February 1939",)
ROTOR_II_SONDER = Rotor(wiring="UEMOATQLSHPKCYFWJZBGVXIDNR",name="II-SONDER",model="Enigma Sonder",date="February 1939",)
ROTOR_III_SONDER = Rotor(wiring="TZHXMBSIPNURJFDKEQVCWGLAOY",name="III-SONDER",model="Enigma Sonder",date="February 1939",)
ROTOR_UKW_SONDER = Reflector(wiring="CIAGSNDRBYTPZFULVHEKOQXWJM",name="UKW-SONDER",model="Enigma Sonder",date="February 1939",)
ROTOR_ETW_SONDER = Rotor(wiring="ABCDEFGHIJKLMNOPQRSTUVWXYZ",name="ETW-SONDER",model="Enigma Sonder",date="February 1939",)

# Enigma K Rotors
ROTOR_I_K = Rotor(wiring="LPGSZMHAEOQKVXRFYBUTNICJDW",notchs="G",name="I-K",model="Enigma K",date="February 1939",)
ROTOR_II_K = Rotor(wiring="SLVGBTFXJQOHEWIRZYAMKPCNDU",notchs="M",name="II-K",model="Enigma K",date="February 1939",)
ROTOR_III_K = Rotor(wiring="CJGDPSHKTURAWZXFMYNQOBVLIE",notchs="V",name="III-K",model="Enigma K",date="February 1939",)
ROTOR_UKW_K = Reflector(wiring="IMETCGFRAYSQBZXWLHKDVUPOJN",name="UKW-K",model="Enigma K",date="February 1939",)
ROTOR_ETW_K = Rotor(wiring="QWERTZUIOASDFGHJKPYXCVBNML",name="ETW-K",model="Enigma K",date="February 1939",)

# Enigma G Rotors, turnover: 'SUVWZABCEFGIKLOPQ', 'STVYZACDFGHKMNQ', 'UWXAEFHKMNR'
ROTOR_I_G = Rotor(wiring="LPGSZMHAEOQKVXRFYBUTNICJDW",notchs="ACDEHIJKMNOQSTWXY",name="I-G",model="Enigma G",date="",)
ROTOR_II_G = Rotor(wiring="SLVGBTFXJQOHEWIRZYAMKPCNDU",notchs="ABDGHIKLNOPSUVY",name="II-G",model="Enigma G",date="",)
ROTOR_III_G = Rotor(wiring="CJGDPSHKTURAWZXFMYNQOBVLIE",notchs="CEFIMNPSUVZ",name="III-G",model="Enigma G",date="",)
ROTOR_UKW_G = Reflector(wiring="IMETCGFRAYSQBZXWLHKDVUPOJN",name="UKW-G",model="Enigma G",date="",)
ROTOR_ETW_G = Rotor(wiring="QWERTZUIOASDFGHJKPYXCVBNML",name="ETW-G",model="Enigma G",date="",)

# Enigma R(ailway) Rotors
ROTOR_I_R = Rotor(wiring="JGDQOXUSCAMIFRVTPNEWKBLZYH",notchs="V",name="I-R",model="Enigma R",date="February 1939",)
ROTOR_II_R = Rotor(wiring="NTZPSFBOKMWRCJDIVLAEYUXHGQ",notchs="M",name="II-R",model="Enigma R",date="February 1939",)
ROTOR_III_R = Rotor(wiring="JVIUBHTCDYAKEQZPOSGXNRMWFL",notchs="G",name="III-R",model="Enigma R",date="February 1939",)
ROTOR_UKW_R = Reflector(wiring="QYHOGNECVPUZTFDJAXWMKISRBL",name="UKW-R",model="Enigma R",date="February 1939",)
ROTOR_ETW_R = Rotor(wiring="QWERTZUIOASDFGHJKPYXCVBNML",name="ETW-R",model="Enigma R",date="February 1939",)

# Swiss K Rotors
ROTOR_I_SK = Rotor(wiring="PEZUOHXSCVFMTBGLRINQJWAYDK",notchs="G",name="I-K",model="Swiss K",date="February 1939",)
ROTOR_II_SK = Rotor(wiring="ZOUESYDKFWPCIQXHMVBLGNJRAT",notchs="M",name="II-K",model="Swiss K",date="February 1939",)
ROTOR_III_SK = Rotor(wiring="EHRVXGAOBQUSIMZFLYNWKTPDJC",notchs="V",name="III-K",model="Swiss K",date="February 1939",)
ROTOR_UKW_SK = Reflector(wiring="IMETCGFRAYSQBZXWLHKDVUPOJN",name="UKW-K",model="Swiss K",date="February 1939",)
ROTOR_ETW_SK = Rotor(wiring="QWERTZUIOASDFGHJKPYXCVBNML",name="ETW-K",model="Swiss K",date="February 1939",)

# Enigma
ROTOR_I = Rotor(wiring="EKMFLGDQVZNTOWYHXUSPAIBRCJ",notchs="R",name="I",model="Enigma 1",date="1930",)
ROTOR_II = Rotor(wiring="AJDKSIRUXBLHWTMCQGZNPYFVOE",notchs="F",name="II",model="Enigma 1",date="1930",)
ROTOR_III = Rotor(wiring="BDFHJLCPRTXVZNYEIWGAKMUSQO",notchs="W",name="III",model="Enigma 1",date="1930",)
ROTOR_IV = Rotor(wiring="ESOVPZJAYQUIRHXLNFTGKDCMWB",notchs="K",name="IV",model="M3 Army",date="December 1938",)
ROTOR_V = Rotor(wiring="VZBRGITYUPSDNHLXAWMJQOFECK",notchs="A",name="V",model="M3 Army",date="December 1938",)
ROTOR_VI = Rotor(wiring="JPGVOUMFYQBENHZRDKASXLICTW",notchs="AN",name="VI",model="M3 & M4 Naval(February 1942)",date="1939",)
ROTOR_VII = Rotor(wiring="NZJHGRCXMYSWBOUFAIVLPEKQDT",notchs="AN",name="VII",model="M3 & M4 Naval(February 1942)",date="1939",)
ROTOR_VIII = Rotor(wiring="FKQHTLXOCBJSPDZRAMEWNIUYGV",notchs="AN",name="VIII",model="M3 & M4 Naval(February 1942)",date="1939",)

# misc & reflectors
ROTOR_Beta = Rotor(
    wiring="LEYJVCNIXWPBQMDRTAKZGFUHOS", name="Beta", model="M4 R2", date="Spring 1941"
)
ROTOR_Gamma = Rotor(
    wiring="FSOKANUERHMBTIYCWLQPZXVGJD", name="Gamma", model="M4 R2", date="Spring 1941"
)
ROTOR_Reflector_A = Reflector(wiring="EJMZALYXVBWFCRQUONTSPIKHGD", name="Reflector A")
ROTOR_Reflector_B = Reflector(wiring="YRUHQSLDPXNGOKMIEBFZCWVJAT", name="Reflector B")
ROTOR_Reflector_C = Reflector(wiring="FVPJIAOYEDRZXWGCTKUQSBNMHL", name="Reflector C")
ROTOR_Reflector_B_Thin = Reflector(
    wiring="ENKQAUYWJICOPBLMDXZVFTHRGS",
    name="Reflector_B_Thin",
    model="M4 R1 (M3 + Thin)",
    date="1940",
)
ROTOR_Reflector_C_Thin = Reflector(
    wiring="RDOBJNTKVEHMLFCWZAXGYIPSUQ",
    name="Reflector_C_Thin",
    model="M4 R1 (M3 + Thin)",
    date="1940",
)
ROTOR_ETW = Rotor(wiring="ABCDEFGHIJKLMNOPQRSTUVWXYZ", name="ETW", model="Enigma 1")

def encrypt(message, keyset, ringset="", show=False):
    # message: text to encipher
    # keyset: 3 letter key value for rotors
    # ringset: 3 letter ring value for rotors, if not given, will be set to keyset
    # return all set of Key-Ring-Cipher tuple with the designated ringset at the end of encoded ciphers
    if ringset == "":
        ringset = keyset

        alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        keys = []
        for x in alphabets:
            for y in alphabets:
                for z in alphabets:
                    keys.append(x + y + z)

        ciphers = []
        for j in range(len(keys)):
            engine = Enigma(ROTOR_UKW_K, ROTOR_I_K, ROTOR_II_K, ROTOR_III_K, key=keys[j], ring=ringset, debug=False)
            encoded = engine.encipher(message).upper()
            idx = len(encoded) - 3
            s = encoded[idx:idx+3:1]
            if s == ringset:
                ciphers.append({'Key':keys[j], 'Ring':ringset, 'Message':message, 'Cipher':encoded})

        if len(ciphers) == 0:
            print("There is no Key-Ring-Cipher tuple with the designated ring, ", ringset)
        else:
            print("Key-Ring-Cipher tuple(s) found: ", str(len(ciphers)))
        if show:
                for x in ciphers: print(x)
    else:
        engine = Enigma(ROTOR_UKW_K, ROTOR_I_K, ROTOR_II_K, ROTOR_III_K, key=keyset, ring=ringset, debug=False)
        encoded = engine.encipher(message).upper()
        ciphers = []
        ciphers.append({'Key':keyset, 'Ring':ringset, 'Message':message, 'Cipher':encoded})
    
    return ciphers

def decrypt(cipher, keyset, ringset="", show=False):
    # message: cipher to plain text
    # keyset: 3 letter key value for rotors
    # ringset: 3 letter ring value for rotors, if not given, last 3 letters of cipher will be used
    # return decoded text
    if ringset == "":
        ringset = cipher[-3:]

    engine = Enigma(ROTOR_UKW_K, ROTOR_I_K, ROTOR_II_K, ROTOR_III_K, key=keyset, ring=ringset, debug=False)
    decoded = engine.encipher(cipher).upper()
    return decoded
