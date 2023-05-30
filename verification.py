import logging
from pyvat import is_vat_number_format_valid


logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

def verify_ico(ico: str) -> bool:
    ico = str(ico).zfill(
        8
    )  # ensure ico is 8 digits long, fill with zeroes if necessary
    if len(ico) != 8 or not ico.isdigit():
        return False

    weights = [8, 7, 6, 5, 4, 3, 2]
    weighted_sum = sum(
        [int(ico[i]) * weights[i] for i in range(7)]
    )  # calculate weighted sum of the first 7 digits

    x = (11 - (weighted_sum % 11)) % 10

    is_ico_ok = (x == int(ico[7]))
    logging.info(f"IČ {ico} is {is_ico_ok}.")
    return is_ico_ok


def verify_vat(vat: str) -> bool:
    stried_vat = str(vat).strip()
    country_code = stried_vat[:2]
    vat_number = stried_vat[2:]
    is_vat_ok = is_vat_number_format_valid(vat_number=vat_number, country_code=country_code)
    logging.info(f"VAT {stried_vat} is {is_vat_ok}.")
    return is_vat_ok




def main():
    pass



if __name__ == "__main__":
    main()
