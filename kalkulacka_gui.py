import math
import tkinter as tk
import tkinter.font as tkfont

SYMBOLY = {"+": "+", "-": "−", "*": "×", "/": "÷"}
MAX_DLZKA = 12
SIRKA_DISPLEJA = 290  # V pixeloch, podľa nej sa zmenšuje písmo

FARBY = {
    "pozadie": "#f2f4f7", "panel": "#ffffff", "text": "#172033", "sive": "#5a6478",
    "klaves": "#e6e9f0", "klaves_nad": "#d8dce7",
    "akcent": "#1f4bd8", "akcent_nad": "#3a63e6", "akcent_text": "#ffffff",
}


def vypocitaj(a, b, operator):
    a, b = float(a), float(b)
    if operator == "+":
        vysledok = a + b
    elif operator == "-":
        vysledok = a - b
    elif operator == "*":
        vysledok = a * b
    elif operator == "/":
        if b == 0:
            raise ZeroDivisionError("Delenie nulou nie je možné.")
        vysledok = a / b
    else:
        raise ValueError(f"Neznáma operácia: {operator}")
    if not math.isfinite(vysledok):
        raise OverflowError("Výsledok je príliš veľký.")
    return vysledok


# Odstráni chyby zaokrúhľovania (0.1 + 0.2 = 0.3) a zbytočné .0
def formatuj(cislo):
    cislo = float(f"{cislo:.12g}")
    if cislo.is_integer() and abs(cislo) < 1e15:
        return str(int(cislo))
    return repr(cislo)


class Kalkulacka(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulačka")
        self.resizable(False, False)
        self.configure(bg=FARBY["pozadie"], padx=16, pady=16)

        self.aktualne = "0"  # Číslo, ktoré sa práve píše, ako text
        self.predchadzajuce = None
        self.operator = None
        self.prepis = False  # Ďalšia číslica začne nové číslo

        ram = tk.Frame(self, bg=FARBY["panel"], padx=14, pady=14)
        ram.pack()

        # Displej
        self.historia = tk.Label(ram, text="", anchor="e", bg=FARBY["panel"],
                                 fg=FARBY["sive"], font=("Segoe UI", 11))
        self.historia.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.pismo = tkfont.Font(family="Segoe UI", size=30, weight="bold")
        self.vysledok = tk.Label(ram, text="0", anchor="e", bg=FARBY["panel"],
                                 fg=FARBY["text"], font=self.pismo, width=1)
        self.vysledok.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        # Tlačidlá ako (text, akcia, typ)
        rozlozenie = [
            [("C", self.vymaz, "funkcia"), ("⌫", self.spat, "funkcia"),
             ("%", self.percento, "funkcia"), ("÷", lambda: self.vyber_operator("/"), "operator")],
            [("7", None, ""), ("8", None, ""), ("9", None, ""),
             ("×", lambda: self.vyber_operator("*"), "operator")],
            [("4", None, ""), ("5", None, ""), ("6", None, ""),
             ("−", lambda: self.vyber_operator("-"), "operator")],
            [("1", None, ""), ("2", None, ""), ("3", None, ""),
             ("+", lambda: self.vyber_operator("+"), "operator")],
            [("±", self.znamienko, "funkcia"), ("0", None, ""),
             (",", self.zadaj_bodku, ""), ("=", self.rovna, "rovna")],
        ]
        for r, riadok in enumerate(rozlozenie, start=2):
            for c, (text, akcia, typ) in enumerate(riadok):
                if akcia is None:  # Číslica
                    akcia = lambda t=text: self.zadaj_cislicu(t)
                self.vytvor_tlacidlo(ram, text, akcia, typ).grid(row=r, column=c, padx=3, pady=3)

        self.bind("<Key>", self.klavesnica)
        self.zobraz()

    def vytvor_tlacidlo(self, rodic, text, akcia, typ):
        bg, fg, hover = FARBY["klaves"], FARBY["text"], FARBY["klaves_nad"]
        vaha = "normal"
        if typ == "operator":
            fg, vaha = FARBY["akcent"], "bold"
        elif typ == "funkcia":
            fg = FARBY["sive"]
        elif typ == "rovna":
            bg, fg, hover, vaha = FARBY["akcent"], FARBY["akcent_text"], FARBY["akcent_nad"], "bold"
        t = tk.Button(rodic, text=text, command=akcia, width=4, height=2, bd=0, relief="flat",
                      bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                      font=("Segoe UI", 15, vaha), cursor="hand2")
        t.bind("<Enter>", lambda e: t.config(bg=hover))
        t.bind("<Leave>", lambda e: t.config(bg=bg))
        return t

    # Ak sa číslo nezmestí, zmenší písmo
    def nastav_vysledok(self, text):
        velkost = 30
        self.pismo.configure(size=velkost)
        while self.pismo.measure(text) > SIRKA_DISPLEJA and velkost > 10:
            velkost -= 1
            self.pismo.configure(size=velkost)
        self.vysledok.config(text=text)

    def zobraz(self):
        self.nastav_vysledok(self.aktualne.replace(".", ","))
        if self.operator and self.predchadzajuce is not None:
            self.historia.config(
                text=f"{self.predchadzajuce.replace('.', ',')} {SYMBOLY[self.operator]}"
            )

    def chyba(self, sprava="Chyba"):
        self.aktualne = sprava
        self.predchadzajuce = None
        self.operator = None
        self.prepis = True
        self.historia.config(text="")
        self.nastav_vysledok(sprava)

    def zadaj_cislicu(self, c):
        if self.aktualne == "Chyba":
            self.aktualne = "0"
        if self.prepis:
            self.aktualne = c
            self.prepis = False
        elif self.aktualne == "0":
            self.aktualne = c
        elif len(self.aktualne.replace("-", "").replace(".", "")) < MAX_DLZKA:
            self.aktualne += c
        self.zobraz()

    def zadaj_bodku(self):
        if self.aktualne == "Chyba" or self.prepis:
            self.aktualne = "0"
            self.prepis = False
        if "." not in self.aktualne:
            self.aktualne += "."
        self.zobraz()

    def vyber_operator(self, operator):
        if self.aktualne == "Chyba":
            return
        # Pri reťazení 2 + 3 x ... sa najprv vyhodnotí 2 + 3
        if self.operator and not self.prepis:
            try:
                self.aktualne = formatuj(vypocitaj(self.predchadzajuce, self.aktualne, self.operator))
            except (ZeroDivisionError, OverflowError):
                return self.chyba()
        self.predchadzajuce = self.aktualne
        self.operator = operator
        self.prepis = True
        self.zobraz()

    def rovna(self):
        if not self.operator or self.predchadzajuce is None:
            return
        try:
            vysledok = vypocitaj(self.predchadzajuce, self.aktualne, self.operator)
        except (ZeroDivisionError, OverflowError):
            return self.chyba()
        self.historia.config(
            text=f"{self.predchadzajuce.replace('.', ',')} {SYMBOLY[self.operator]} "
                 f"{self.aktualne.replace('.', ',')} ="
        )
        self.aktualne = formatuj(vysledok)
        self.predchadzajuce = None
        self.operator = None
        self.prepis = True
        self.nastav_vysledok(self.aktualne.replace(".", ","))

    def vymaz(self):
        self.aktualne = "0"
        self.predchadzajuce = None
        self.operator = None
        self.prepis = False
        self.historia.config(text="")
        self.zobraz()

    def spat(self):
        if self.prepis or self.aktualne == "Chyba":
            return
        a = self.aktualne
        if len(a) > 1 and not (len(a) == 2 and a.startswith("-")):
            self.aktualne = a[:-1]
        else:
            self.aktualne = "0"
        self.zobraz()

    def percento(self):
        if self.aktualne == "Chyba":
            return
        self.aktualne = formatuj(float(self.aktualne) / 100)
        self.zobraz()

    def znamienko(self):
        if self.aktualne in ("Chyba", "0"):
            return
        a = self.aktualne
        self.aktualne = a[1:] if a.startswith("-") else "-" + a
        self.zobraz()

    def klavesnica(self, e):
        if e.char.isdigit():
            self.zadaj_cislicu(e.char)
        elif e.char in (".", ","):
            self.zadaj_bodku()
        elif e.char in SYMBOLY:
            self.vyber_operator(e.char)
        elif e.keysym in ("Return", "KP_Enter") or e.char == "=":
            self.rovna()
        elif e.keysym == "BackSpace":
            self.spat()
        elif e.keysym == "Escape":
            self.vymaz()


if __name__ == "__main__":
    Kalkulacka().mainloop()
