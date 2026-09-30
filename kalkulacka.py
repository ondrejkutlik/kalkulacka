import re

CISLO = r"-?\d+(?:[.,]\d+)?"
PRIKLAD = re.compile(rf"^\s*({CISLO})\s*(\*\*|[+\-*/%])\s*({CISLO})\s*$")
POKRACOVANIE = re.compile(rf"^\s*(\*\*|[+\-*/%])\s*({CISLO})\s*$")


def na_cislo(text):
    return float(text.replace(",", "."))


def vypocitaj(a, operator, b):
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "**":
        return a ** b
    if operator in ("/", "%"):
        if b == 0:
            raise ZeroDivisionError("Delenie nulou nie je možné.")
        return a / b if operator == "/" else a % b
    raise ValueError(f"Neznáma operácia: {operator}")


def formatuj(cislo):
    if isinstance(cislo, complex):
        return "výsledok nie je reálne číslo"
    if cislo == int(cislo):
        return str(int(cislo))
    return str(round(cislo, 10))


def main():
    print("Kalkulačka")
    print("Operácie: +  -  *  /  **  %      Ukončenie: q\n")

    posledny = None

    while True:
        text = input("Príklad: ").strip()

        if text.lower() in ("q", "quit", "koniec", "exit"):
            print("Maj sa!")
            break
        if not text:
            continue

        zhoda = PRIKLAD.match(text)
        if zhoda:
            a, operator, b = na_cislo(zhoda[1]), zhoda[2], na_cislo(zhoda[3])
        else:
            zhoda = POKRACOVANIE.match(text)
            if zhoda and posledny is not None:
                a, operator, b = posledny, zhoda[1], na_cislo(zhoda[2])
            else:
                print("Nerozumiem. Skús napríklad:  2 + 3\n")
                continue

        try:
            vysledok = vypocitaj(a, operator, b)
        except (ZeroDivisionError, ValueError) as chyba:
            print(f"Chyba: {chyba}\n")
            continue
        except OverflowError:
            print("Chyba: výsledok je príliš veľký.\n")
            continue

        posledny = vysledok if not isinstance(vysledok, complex) else None
        print(f"= {formatuj(vysledok)}\n")


if __name__ == "__main__":
    main()