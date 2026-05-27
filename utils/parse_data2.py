import pyparsing as pp

def parse_mass_data(filepath):
    # 1. Disabilitiamo il salto automatico degli spazi
    pp.ParserElement.setDefaultWhitespaceChars("")

    # Funzione per pulire le stringhe mantenendo i casi vuoti
    def clean_str(t):
        return t[0].strip()

    # Parse Action: converte in numero, gestisce il '#' e il '*'
    def convert_numeric(s, loc, toks):
        val = toks[0].strip()
        # Se il campo è vuoto o è un asterisco (dato mancante)
        if not val or val == '*':
            return None
        
        # Sostituiamo il # con il punto decimale
        val = val.replace('#', '.')
        
        try:
            # Se ha il punto, è un float, altrimenti un int
            return float(val) if '.' in val else int(val)
        except ValueError:
            # Se fallisce (es. se sta leggendo l'header "MASS EXCESS"), 
            # forziamo un errore di PyParsing per saltare la riga
            raise pp.ParseException(s, loc, f"Valore numerico non valido: '{val}'")

    # Helper: crea un campo di lunghezza esatta per le stringhe
    def Field(length):
        return pp.Regex(rf".{{{length}}}").setParseAction(clean_str)

    # Helper: crea un campo numerico di lunghezza esatta
    def NumField(length):
        return pp.Regex(rf".{{{length}}}").setParseAction(convert_numeric)

    # 2. Costruzione della grammatica riga per riga
    # Basata sul formato FORTRAN: a1,i3,i5,i5,i5,1x,a3,a4,1x,f14.6,f12.6,f13.5,1x,f10.5,1x,a2,f13.5,f11.5,1x,i3,1x,f13.6,f12.6
    line_parser = (
        Field(1)("cc") +                            # a1: Control character
        NumField(3)("NZ") +                         # i3: N-Z
        NumField(5)("N") +                          # i5: Neutroni
        NumField(5)("Z") +                          # i5: Protoni
        NumField(5)("A") +                          # i5: Massa
        pp.Suppress(pp.Regex(r'.{1}')) +            # 1x: Spazio vuoto
        Field(3)("element") +                       # a3: Simbolo elemento
        Field(4)("origin") +                        # a4: Origine
        pp.Suppress(pp.Regex(r'.{1}')) +            # 1x
        NumField(14)("mass_excess") +               # f14.6
        NumField(12)("mass_excess_unc") +           # f12.6
        NumField(13)("binding_energy") +            # f13.5
        pp.Suppress(pp.Regex(r'.{1}')) +            # 1x
        NumField(10)("binding_energy_unc") +        # f10.5
        pp.Suppress(pp.Regex(r'.{1}')) +            # 1x
        Field(2)("beta_decay_type") +               # a2: Es. B-
        NumField(13)("beta_decay_energy") +         # f13.5
        NumField(11)("beta_decay_energy_unc") +     # f11.5
        pp.Suppress(pp.Regex(r'.{1}')) +            # 1x
        NumField(3)("atomic_mass_int") +            # i3
        pp.Suppress(pp.Regex(r'.{1}')) +            # 1x
        NumField(13)("atomic_mass_micro") +         # f13.6
        pp.restOfLine.setParseAction(convert_numeric)("atomic_mass_unc") # f12.6 alla fine della riga
    )

    data = []
    
    # 3. Lettura del file e applicazione del parser
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            
            # Pad della stringa. Spesso a fine file gli spazi vuoti saltano, ma per 
            # il nostro regex esatto è bene avere la lunghezza corretta dell'intera riga
            if len(line) < 135:
                line = line.ljust(135)
                
            try:
                # Applica il parser
                parsed = line_parser.parseString(line)
                data.append(parsed.asDict())
            except pp.ParseException:
                # Ignora automaticamente l'header e righe non conformi ai numeri previsti
                continue
                
    return data


if __name__ == "__main__":
    # Esempio di utilizzo
    parsed_data = parse_mass_data("data/mass_1.mas20.txt")
    
    with open("parsed_data.json", "w", encoding="utf-8") as f:
        import json
        json.dump(parsed_data, f, indent=4)

