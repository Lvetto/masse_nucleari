
DATA_DIR = "data/mass_1.mas20.txt"

def clean_empty_strings(lst):
    return [x for x in lst if x != ""]


def load_data():
    with open(DATA_DIR, "r") as f:
        data = f.read().splitlines()

    header = clean_empty_strings(data[0].split(" "))
    units = clean_empty_strings(data[1].split(" "))



    data = data[2:]
    data = [i[1:] for i in data]

    NZ__INDEX = 0
    N_INDEX = 1
    Z_INDEX = 2
    A_INDEX = 3
    EL_INDEX = 4
    ORIGIN__INDEX = 5
    MASS_EXCESS_INDEX = 6
    MASS_EXCESS_ERROR_INDEX = 7
    BINDING_ENERGY_INDEX = 8
    BINDING_ENERGY_ERROR_INDEX = 9
    DECAY_MODE_INDEX = 10
    DECAY_ENERGY_INDEX = 11
    DECAY_ENERGY_ERROR_INDEX = 12

    UNKNOWN_INDEX = 13

    ATOMIC_MASS_INDEX = 14
    ATOMIC_MASS_ERROR_INDEX = 15

    cols_to_check_for_pound = [BINDING_ENERGY_INDEX, BINDING_ENERGY_ERROR_INDEX]

    out_data = {
        "N" : [],
        "Z" : [],
        "A" : [],
        "EL" : [],
        "BINDING_ENERGY" : [],
        "BINDING_ENERGY_ERROR" : []
    }

    skipped_lines = 0

    for n, i in enumerate(data):

        use_line = True

        #if "*" in i or "#" in i:
        #    use_line = False
        #    continue

        i = clean_empty_strings(i.split(" "))
        
        if not use_line:
            continue

        if len(i) < 16:
            print(f"Line {n+3} has less than 16 columns: {i}")
            
        if len(i) == 15:
            i.insert(ORIGIN__INDEX, "")

        try:

            N = int(i[N_INDEX])
            Z = int(i[Z_INDEX])
            A = int(i[A_INDEX])

            EL = i[EL_INDEX] # già stringa

            BINDING_ENERGY = float(i[BINDING_ENERGY_INDEX])
            BINDING_ENERGY_ERROR = float(i[BINDING_ENERGY_ERROR_INDEX])

            # Append the processed row to the output data
            out_data["N"].append(N)
            out_data["Z"].append(Z)
            out_data["A"].append(A)
            out_data["EL"].append(EL)
            out_data["BINDING_ENERGY"].append(BINDING_ENERGY)
            out_data["BINDING_ENERGY_ERROR"].append(BINDING_ENERGY_ERROR)
        
        except ValueError as e:
            print(f"Error processing line {n+3}: {i}")
            print(f"Error message: {e}")
            continue
    
    out_dict = {
        "header": header,
        "units": units,
        "data": out_data
    }


    return out_dict


if __name__ == "__main__":
    data = load_data()
    header = data["header"]
    units = data["units"]
    data = data["data"]

    for key, value in data.items():
        print(f"{key}: {len(value)}")

