from regrippy import BasePlugin, PluginResult, mactime
from Registry.Registry import RegistryValueNotFoundException


class Plugin(BasePlugin):
    """List keyboard languages for the current user"""

    __REGHIVE__ = "NTUSER.DAT"

    def run(self):
        preload = self.open_key("Keyboard Layout\\Preload")
        substitutes = self.open_key("Keyboard Layout\\Substitutes")

        if not preload or not substitutes:
            return

        for preload_value in preload.values():
            preload_txt = preload_value.value()

            try:
                subs = substitutes.value(preload_txt)
            except RegistryValueNotFoundException:
                subs = None

            r = PluginResult(key=preload, value=preload_value)
            r.custom["substitute"] = subs
            yield r

    def display_human(self, result):
        subs_txt = self.get_subsitution_string(result.custom["substitute"])
        print(self.get_lang_name(result.value_data) + subs_txt)

    def display_machine(self, result):
        username = self.guess_username()
        subs_txt = self.get_subsitution_string(result.custom["substitute"])
        print(
            mactime(
                name=f"{username}\t{self.get_lang_name(result.value_data)}{subs_txt}",
                mtime=result.mtime,
            )
        )

    def get_lang_name(self, code):
        lang_code = int(code, 16) & (~0xDFF00000)
        if lang_code not in languageCodes.keys():
            return f"Unknown: {code}"
        else:
            return languageCodes[lang_code]

    def get_subsitution_string(self, value):
        subs_txt = ""
        if value:
            subs_txt = " / " + self.get_lang_name(value.value())
        return subs_txt


# Extracted from a Windows 10 1903 + data from Magnum DB
languageCodes = {
    0x00000401: "Arabic (101)",
    0x00000402: "Bulgarian (Typewriter)",
    0x00000404: "Chinese (Traditional) - US Keyboard",
    0x00000405: "Czech",
    0x00000406: "Danish",
    0x00000407: "German",
    0x00000408: "Greek",
    0x00000409: "US",
    0x0000040A: "Spanish",
    0x0000040B: "Finnish",
    0x0000040C: "French",
    0x0000040D: "Hebrew",
    0x0000040E: "Hungarian",
    0x0000040F: "Icelandic",
    0x00000410: "Italian",
    0x00000411: "Japanese",
    0x00000412: "Korean",
    0x00000413: "Dutch",
    0x00000414: "Norwegian",
    0x00000415: "Polish (Programmers)",
    0x00000416: "Portuguese (Brazilian ABNT)",
    0x00000418: "Romanian (Legacy)",
    0x00000419: "Russian",
    0x0000041A: "Standard",
    0x0000041B: "Slovak",
    0x0000041C: "Albanian",
    0x0000041D: "Swedish",
    0x0000041E: "Thai Kedmanee",
    0x0000041F: "Turkish Q",
    0x00000420: "Urdu",
    0x00000422: "Ukrainian",
    0x00000423: "Belarusian",
    0x00000424: "Slovenian",
    0x00000425: "Estonian",
    0x00000426: "Latvian",
    0x00000427: "Lithuanian IBM",
    0x00000428: "Tajik",
    0x00000429: "Persian",
    0x0000042A: "Vietnamese",
    0x0000042B: "Armenian Eastern",
    0x0000042C: "Azeri Latin",
    0x0000042E: "Sorbian Standard (Legacy)",
    0x0000042F: "Macedonian (FYROM)",
    0x00000432: "Setswana",
    0x00000437: "Georgian",
    0x00000438: "Faeroese",
    0x00000439: "Devanagari - INSCRIPT",
    0x0000043A: "Maltese 47-Key",
    0x0000043B: "Norwegian with Sami",
    0x0000043F: "Kazakh",
    0x00000440: "Kyrgyz Cyrillic",
    0x00000442: "Turkmen",
    0x00000444: "Tatar (Legacy)",
    0x00000445: "Bengali",
    0x00000446: "Punjabi",
    0x00000447: "Gujarati",
    0x00000448: "Oriya",
    0x00000449: "Tamil",
    0x0000044A: "Telugu",
    0x0000044B: "Kannada",
    0x0000044C: "Malayalam",
    0x0000044D: "Assamese - INSCRIPT",
    0x0000044E: "Marathi",
    0x00000450: "Mongolian Cyrillic",
    0x00000451: "Tibetan (PRC)",
    0x00000452: "United Kingdom Extended",
    0x00000453: "Khmer",
    0x00000454: "Lao",
    0x0000045A: "Syriac",
    0x0000045B: "Sinhala",
    0x0000045C: "Cherokee Nation",
    0x00000461: "Nepali",
    0x00000463: "Pashto (Afghanistan)",
    0x00000465: "Divehi Phonetic",
    0x00000468: "Hausa",
    0x0000046A: "Yoruba",
    0x0000046C: "Sesotho sa Leboa",
    0x0000046D: "Bashkir",
    0x0000046E: "Luxembourgish",
    0x0000046F: "Greenlandic",
    0x00000470: "Igbo",
    0x00000474: "Guarani",
    0x00000475: "Hawaiian",
    0x00000480: "Uyghur (Legacy)",
    0x00000481: "Maori",
    0x00000485: "Sakha",
    0x00000488: "Wolof",
    0x00000492: "Central Kurdish",
    0x00000804: "Chinese (Simplified) - US Keyboard",
    0x00000807: "Swiss German",
    0x00000809: "United Kingdom",
    0x0000080A: "Latin American",
    0x0000080C: "Belgian French",
    0x00000813: "Belgian (Period)",
    0x00000816: "Portuguese",
    0x0000081A: "Serbian (Latin)",
    0x0000082C: "Azeri Cyrillic",
    0x0000083B: "Swedish with Sami",
    0x00000843: "Uzbek Cyrillic",
    0x00000850: "Mongolian (Mongolian Script)",
    0x0000085D: "Inuktitut - Latin",
    0x0000085F: "Central Atlas Tamazight",
    0x00000C04: "Chinese (Traditional, Hong Kong S.A.R.) - US Keyboard",
    0x00000C0A: "Spanish (International)",  # MagnumDB
    0x00000C0C: "Canadian French (Legacy)",
    0x00000C1A: "Serbian (Cyrillic)",
    0x00000C51: "Dzongkha",
    0x00001004: "Chinese (Simplified, Singapore) - US Keyboard",
    0x00001009: "Canadian French",
    0x0000100C: "Swiss French",
    0x0000105F: "Tifinagh (Basic)",
    0x00001404: "Chinese (Traditional, Macao S.A.R.) - US Keyboard",
    0x00001809: "Irish",
    0x0000201A: "Bosnian (Cyrillic)",
    0x00004009: "India",
    0x00010401: "Arabic (102)",
    0x00010402: "Bulgarian (Latin)",
    0x00010405: "Czech (QWERTY)",
    0x00010407: "German (IBM)",
    0x00010408: "Greek (220)",
    0x00010409: "United States-Dvorak",
    0x0001040A: "Spanish Variation",
    0x0001040E: "Hungarian 101-key",
    0x00010410: "Italian (142)",
    0x00010415: "Polish (214)",
    0x00010416: "Portuguese (Brazilian ABNT2)",
    0x00010418: "Romanian (Standard)",
    0x00010419: "Russian (Typewriter)",
    0x0001041B: "Slovak (QWERTY)",
    0x0001041E: "Thai Pattachote",
    0x0001041F: "Turkish F",
    0x00010426: "Latvian (QWERTY)",
    0x00010427: "Lithuanian",
    0x0001042B: "Armenian Western",
    0x0001042C: "Azerbaijani (Standard)",
    0x0001042E: "Sorbian Extended",
    0x0001042F: "Macedonian (FYROM) - Standard",
    0x00010437: "Georgian (QWERTY)",
    0x00010439: "Hindi Traditional",
    0x0001043A: "Maltese 48-Key",
    0x0001043B: "Sami Extended Norway",
    0x00010444: "Tatar",
    0x00010445: "Bengali - INSCRIPT (Legacy)",
    0x00010451: "Tibetan (PRC) - Updated",
    0x00010453: "Khmer (NIDA)",
    0x0001045A: "Syriac Phonetic",
    0x0001045B: "Sinhala - Wij 9",
    0x0001045C: "Cherokee Nation Phonetic",
    0x0001045D: "Inuktitut - Naqittaut",
    0x00010465: "Divehi Typewriter",
    0x00010480: "Uyghur",
    0x0001080C: "Belgian (Comma)",
    0x0001083B: "Finnish with Sami",
    0x00010850: "Traditional Mongolian (Standard)",
    0x00010C00: "Myanmar (Phonetic order)",
    0x00011009: "Canadian Multilingual Standard",
    0x0001105F: "Tifinagh (Full)",
    0x00011809: "Gaelic",
    0x00020401: "Arabic (102) AZERTY",
    0x00020402: "Bulgarian (Phonetic)",
    0x00020405: "Czech Programmers",
    0x00020408: "Greek (319)",
    0x00020409: "United States-International",
    0x0002040D: "Hebrew (Standard)",
    0x00020418: "Romanian (Programmers)",
    0x00020419: "Russian - Mnemonic",
    0x0002041E: "Thai Kedmanee (non-ShiftLock)",
    0x00020422: "Ukrainian (Enhanced)",
    0x00020426: "Latvian (Standard)",
    0x00020427: "Lithuanian Standard",
    0x0002042B: "Armenian Phonetic",
    0x0002042E: "Sorbian Standard",
    0x00020437: "Georgian (Ergonomic)",
    0x00020445: "Bengali - INSCRIPT",
    0x00020449: "Tamil 99",
    0x0002083B: "Sami Extended Finland-Sweden",
    0x00020C00: "New Tai Lue",
    0x00030402: "Bulgarian",
    0x00030408: "Greek (220) Latin",
    0x00030409: "United States-Dvorak for left hand",
    0x0003041E: "Thai Pattachote (non-ShiftLock)",
    0x0003042B: "Armenian Typewriter",
    0x00030437: "Georgian Ministry of Education and Science Schools",
    0x00030C00: "Tai Le",
    0x00040402: "Bulgarian (Phonetic Traditional)",
    0x00040408: "Greek (319) Latin",
    0x00040409: "United States-Dvorak for right hand",
    0x00040437: "Georgian (Old Alphabets)",
    0x00040C00: "Ogham",
    0x00050408: "Greek Latin",
    0x00050409: "US English Table for IBM Arabic 238_L",
    0x00050429: "Persian (Standard)",
    0x00060408: "Greek Polytonic",
    0x00070C00: "Lisu (Basic)",
    0x00080C00: "Lisu (Standard)",
    0x00090C00: "N’Ko",
    0x000A0C00: "Phags-pa",
    0x000B0C00: "Buginese",
    0x000C0C00: "Gothic",
    0x000D0C00: "Ol Chiki",
    0x000E0C00: "Osmanya",
    0x000F0C00: "Old Italic",
    0x00100C00: "Sora",
    0x00110C00: "Javanese",
    0x00120C00: "Futhark",
    0x00130C00: "Myanmar (Visual Order)",
    0x00140C00: "ADLaM",
    0x00150C00: "Osage",
}
