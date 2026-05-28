import pandas as pd

COLSPECS = [
    (0,  1),   # cc (Fortran control char)
    (1,  4),   # N-Z
    (4,  9),   # N
    (9,  14),  # Z
    (14, 19),  # A
    (20, 23),  # EL (element symbol)
    (23, 27),  # origin flag
    (29, 43),  # mass excess (keV)
    (43, 55),  # mass excess uncertainty
    (55, 68),  # binding energy/A (keV)
    (69, 79),  # binding energy uncertainty
    (80, 82),  # beta decay type
    (82, 95),  # beta decay energy (keV)
    (95, 106), # beta decay uncertainty
    (107, 110),# atomic mass integer part (u)
    (111, 124),# atomic mass fractional part (micro-u)
    (124, 136),# atomic mass uncertainty (micro-u)
]

NAMES = [
    "cc", "NZ", "N", "Z", "A", "EL", "origin",
    "mass_excess_keV", "mass_excess_unc",
    "binding_energy_keV", "binding_energy_unc",
    "beta_type", "beta_energy_keV", "beta_energy_unc",
    "atomic_mass_int_u",
    "atomic_mass_frac_uU", "atomic_mass_unc_uU",
]

def _normalize_col(series: pd.Series) -> pd.Series:
    """Converte in float; valori contenenti '#' (stime) diventano NaN."""
    return (
        series.astype(str)
        .str.replace(r"\S*#\S*", "nan", regex=True)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
    )

def read_file(filepath: str) -> pd.DataFrame:
    with open(filepath, "r") as f:
        lines = f.readlines()

    data_start = next(
        i for i, line in enumerate(lines)
        if line.startswith("....+....1")
    ) + 1

    df = pd.read_fwf(
        filepath,
        colspecs=COLSPECS,
        names=NAMES,
        skiprows=data_start,
        na_values=["*"],
    )

    # Normalizza tutte le colonne numeriche (#→.)
    str_cols = {"cc", "EL", "origin", "beta_type"}
    for col in df.columns:
        if col not in str_cols:
            df[col] = _normalize_col(df[col])

    # Combina parte intera e frazionaria → massa atomica in micro-u
    df["atomic_mass_uU"] = df["atomic_mass_int_u"] * 1_000_000 + df["atomic_mass_frac_uU"]

    # Rimuovi le colonne intermedie ora che sono combinate
    df = df.drop(columns=["atomic_mass_int_u", "atomic_mass_frac_uU"])

    return df

def extract_relevant_data(df: pd.DataFrame) -> pd.DataFrame:
    
    relevant_cols = ["A", "Z", "N", "EL", "binding_energy_keV", "binding_energy_unc"]
    relevant_df = df[relevant_cols].copy()

    # elimina righe con dati mancanti
    relevant_df = relevant_df.dropna(how="any")

    # resetta indici dopo la rimozione
    relevant_df = relevant_df.reset_index(drop=True)

    return relevant_df


if __name__ == "__main__":
    df = read_file("data/mass.txt")
    df = extract_relevant_data(df)

    print(df["binding_energy_keV"])


