import pandas as pd

COLSPECS = [
    (0, 1),     # Fortran control character
    (1, 4),     # N-Z
    (4, 9),     # N
    (9, 14),    # Z
    (14, 19),   # A
    (20, 23),   # Element symbol
    (23, 27),   # Origin
    (28, 42),   # Mass excess [keV]
    (42, 54),   # Mass excess uncertainty
    (54, 67),   # Specific BE [keV]
    (68, 78),   # Specific BE uncertainty
    (79, 81),   # Beta decay type
    (81, 94),   # Beta decay energy [keV]
    (94, 105),  # Beta decay energy uncertainty
    (106, 109), # Atomic mass' integer part [u]
    (110, 123), # Atomic mass' fractional part [micro-u]
    (123, 135)  # Atomic mass' uncertainty [micro-u]
]

NAMES = [
    "cc", "NZ", "N", "Z", "A", "el", "origin",
    "mass_excess", "mass_excess_err",
    "binding_energy", "binding_energy_err",
    "beta_type", "beta_energy", "beta_energy_err",
    "atomic_mass_int", "atomic_mass_frac", "atomic_mass_frac_err",
]

def _normalize_col(series: pd.Series) -> pd.Series:
    """Converte le stringhe di numeri in float. Valori contenenti '#' (stime) diventano NaN."""
    return (
        series.astype(str)
        .str.replace(r"\S*#\S*", "nan", regex=True)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
    )

def read_file(filepath: str) -> pd.DataFrame:
    """Parser ad-hoc per il file 'mass.mas20'. Le masse atomiche vengono combinate, con unità micro-u."""
    # Apriamo lo stream:
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Scartiamo l'header:
    data_start = next(
        i for i, line in enumerate(lines)
        if line.startswith("....+....1")
    ) + 7

    # Lasciamo che pandas converta il file fortran:
    df = pd.read_fwf(
        filepath,
        colspecs=COLSPECS,
        names=NAMES,
        skiprows=data_start,
        na_values=["*"]
    )

    # Leggiamo i numeri come tali:
    str_cols = {"cc", "el", "origin", "beta_type"}
    int_cols = {"NZ", "N", "Z", "A"}
    for col in df.columns:
        if col in int_cols:
            df[col] = pd.to_numeric(df[col]).astype(int)
        elif col not in str_cols:
            df[col] = _normalize_col(df[col])

    # Calcoliamo le atomic mass totali in micro-u:
    df["atomic_mass"] = df["atomic_mass_int"] * 1e6 + df["atomic_mass_frac"]
    df["atomic_mass_err"] = df["atomic_mass_frac_err"]
    df = df.drop(columns=["atomic_mass_int", "atomic_mass_frac", "atomic_mass_frac_err"])

    return df

def extract_relevant_data(df: pd.DataFrame) -> pd.DataFrame:
    """Estrae solo le colonne che servono alla nostra analisi."""
    relevant_cols = ["A", "Z", "N", "el", "binding_energy", "binding_energy_err"]
    relevant_df = df[relevant_cols].copy()

    # Eliminiamo le righe contenenti NaN:
    relevant_df = relevant_df.dropna(how="any")
    relevant_df = relevant_df.reset_index(drop=True)

    return relevant_df


# Per testare il parsing da terminale:
if __name__ == "__main__":
    df = read_file("mass.mas20.txt")
    df = extract_relevant_data(df)
    print(df.head())


