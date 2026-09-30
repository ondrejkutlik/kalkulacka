"""Kalkulačka – grafická verzia (tkinter).

Python prepis webovej aplikácie kalkulacka.html.
Stavový automat bez použitia eval(). Ovládanie myšou aj klávesnicou
(číslice, + - * /, Enter alebo =, Backspace, Esc, bodka alebo čiarka).
Spustenie:  python kalkulacka_gui.py
"""

import math
import tkinter as tk
import tkinter.font as tkfont

SYMBOLY = {"+": "+", "-": "−", "*": "×", "/": "÷"}
MAX_DLZKA = 12
SIRKA_DISPLEJA = 290  # px, na zmenšovanie písma

FARBY = {
    "bg": "#f2f4f7", "surface": "#ffffff", "ink": "#172033", "muted": "#5a6478",
    "key": "#e6e9f0", "key_hover": "#d8dce7", "accent": "#1f4bd8", "accent_ink": "#ffffff",
}


def vypocitaj(a, b, op):
    a, b = float(a), float(b)
    if op == "+":
        vysledok = a + b
    elif op == "-":
        vysledok = a - b
    elif op == "*":
        vysledok = a * b
    elif op == "/":
        if b == 0:
            raise ZeroDivisionError("Delenie nulou")
        vysledok = a / b
    else:
        raise ValueError(f"Neznáma operácia: {op}")
    if not math.isfinite(vysledok):
        raise OverflowError("Výsledok je príliš veľký")
    return vysledok


def formatuj(cislo):
    """Odstráni chyby zaokrúhľovania (0.1 + 0.2 -> 0.3) a zbytočné .0."""
    cislo = float(f"{cislo:.12g}")
    if cislo.is_integer() and abs(cislo) < 1e15:
        return str(int(cislo))
    return repr(cislo)


class Kalkulacka(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulačka")
        self.resizable(False, False)
        self.configure(bg=FARBY["bg"], padx=16, pady=16)

        self.aktualne = "0"       # číslo, ktoré sa práve píše (ako text)
        self.predchadzajuce = None
        self.operator = None
        self.prepis = False       # True = ďalšia číslica začne nové číslo

        ram = tk.Frame(self, bg=FARBY["surface"], padx=14, pady=14)
        ram.pack()

        # Displej
        self.historia = tk.Label(ram, text="", anchor="e", bg=FARBY["surface"],
                                 fg=FARBY["muted"], font=("Segoe UI", 11))
        self.historia.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.pismo = tkfont.Font(family="Segoe UI", size=30, weight="bold")
        self.vysledok = tk.Label(ram, text="0", anchor="e", bg=FARBY["surface"],
                                 fg=FARBY["ink"], font=self.pismo, width=1)
        self.vysledok.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        # Tlačidlá: (text, akcia, typ)
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
                if akcia is None:  # číslica
                    akcia = lambda t=text: self.zadaj_cislicu(t)
                self._tlacidlo(ram, text, akcia, typ).grid(row=r, column=c, padx=3, pady=3)

        self.bind("<Key>", self.klavesnica)
        self.zobraz()

    def _tlacidlo(self, rodic, text, akcia, typ):
        bg, fg, hover = FARBY["key"], FARBY["ink"], FARBY["key_hover"]
        vaha = "normal"
        if typ == "operator":
            fg, vaha = FARBY["accent"], "bold"
        elif typ == "funkcia":
            fg = FARBY["muted"]
        elif typ == "rovna":
            bg, fg, hover, vaha = FARBY["accent"], FARBY["accent_ink"], "#3a63e6", "bold"
        t = tk.Button(rodic, text=text, command=akcia, width=4, height=2, bd=0, relief="flat",
                      bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                      font=("Segoe UI", 15, vaha), cursor="hand2")
        t.bind("<Enter>", lambda e: t.config(bg=hover))
        t.bind("<Leave>", lambda e: t.config(bg=bg))
        return t

    # ---------- zobrazenie ----------
    def nastav_vysledok(self, text):
        """Zobrazí text a v prípade potreby zmenší písmo, aby sa číslo zmestilo."""
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

    # ---------- akcie ----------
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

    def vyber_operator(self, op):
        if self.aktualne == "Chyba":
            return
        # Reťazenie: 2 + 3 × ... vyhodnotí najprv 2 + 3
        if self.operator and not self.prepis:
            try:
                self.aktualne = formatuj(vypocitaj(self.predchadzajuce, self.aktualne, self.operator))
            except (ZeroDivisionError, OverflowError):
                return self.chyba()
        self.predchadzajuce = self.aktualne
        self.operator = op
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

    # ---------- klávesnica ----------
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
