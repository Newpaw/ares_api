import os
import requests
import logging
import redis
import json

from dataclasses import dataclass
from typing import List, Optional
import pandas as pd



logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

redis_host_name = os.environ.get("REDIS_HOST_NAME", "localhost")

try:
    redis_instance = redis.Redis(host=redis_host_name, port=6379, db=0)
except redis.RedisError as e:
    logging.error(f"Nepodařilo se připojit k Redisu: {e}")
    redis_instance = None


# Rozšíření slovníku pro právní formy
legal_forms = {
    "100": "Podnikající fyzická osoba tuzemská fyzická osoba",
    "111": "Veřejná obchodní společnost",
    "112": "Společnost s ručením omezeným",
    "113": "Společnost komanditní",
    "114": "Společnost komanditní na akcie",
    "115": "Společný podnik",
    "116": "Zájmové sdružení",
    "117": "Nadace",
    "118": "Nadační fond",
    "121": "Akciová společnost",
    "131": "Svépomocné zemědělské družstvo",
    "141": "Obecně prospěšná společnost",
    "145": "Společenství vlastníků jednotek",
    "151": "Komoditní burza",
    "152": "Garanční fond obchodníků s cennými papíry",
    "161": "Ústav",
    "201": "Zemědělské družstvo",
    "205": "Družstvo",
    "211": "Družstevní podnik zemědelský",
    "231": "Výrobní družstvo",
    "232": "Spotřební družstvo",
    "233": "Bytové družstvo",
    "234": "Jiné družstvo",
    "241": "Družstevní podnik (s 1 zakladatelem)",
    "242": "Společný podnik (s více zakladateli)",
    "251": "Zájmová organizace družstev",
    "261": "Společná zájmová organizace družstev",
    "301": "Státní podnik",
    "302": "Národní podnik",
    "311": "Státní banka československá",
    "312": "Banka-státní peněžní ústav",
    "313": "Česká národní banka",
    "314": "Česká konsolidační agentura",
    "325": "Organizační složka státu",
    "326": "Stálý rozhodčí soud",
    "331": "Příspěvková organizace zřízená územním samosprávným celkem",
    "332": "Státní příspěvková organizace",
    "333": "Státní příspěvková organizace ostatní",
    "341": "Státní hospodářská organizace řízená okresním úřadem",
    "343": "Obecní podnik",
    "351": "Československé státní dráhy-státní organizace",
    "352": "Správa železniční dopravní cesty, státní organizace",
    "353": "Rada pro veřejný dohled nad auditem",
    "361": "Veřejnoprávní instituce",
    "362": "Česká tisková kancelář",
    "381": "Státní fond ze zákona",
    "382": "Státní fond ze zákona nezapisující se do obchodního rejstříku",
    "391": "Zdravotní pojišťovna (mimo VZP)",
    "392": "Všeobecná zdravotní pojišťovna",
    "401": "Sdružení mezinárodního obchodu",
    "411": "Podnik se zahraniční majetkovou účastí",
    "421": "Odštěpný závod zahraniční právnické osoby",
    "422": "Organizační složka zahraničního nadačního fondu",
    "423": "Organizační složka zahraniční nadace",
    "424": "Zahraniční fyzická osoba fyzická osoba",
    "425": "Odštěpný závod zahraniční fyzické osoby",
    "426": "Zastoupení zahraniční banky",
    "441": "Podnik zahraničního obchodu",
    "442": "Účelová zahraničně obchodní organizace",
    "501": "Odštěpný závod",
    "521": "Samostatná drobná provozovna (obecního úřadu)",
    "525": "Vnitřní organizační jednotka organizační složky státu",
    "601": "Vysoká škola (veřejná, státní)",
    "641": "Školská právnická osoba",
    "661": "Veřejná výzkumná instituce",
    "671": "Veřejné neziskové ústavní zdravotnické zařízení",
    "701": "Občanské sdružení",
    "703": "Odborová organizace a organizace zaměstnavatelů",
    "704": "Zvláštní organizace pro zastoupení českých zájmů v mezinárodních nevládních organizacích",
    "705": "Podnik nebo hospodářské zařízení sdružení",
    "706": "Spolek",
    "707": "Odborová organizace",
    "708": "Organizace zaměstnavatelů",
    "711": "Politická strana, politické hnutí",
    "715": "Podnik nebo hospodářské zařízení politické strany",
    "721": "Církve a náboženské společnosti",
    "722": "Evidované církevní právnické osoby",
    "723": "Svazy církví a náboženských společností",
    "731": "Organizační jednotka občanského sdružení",
    "733": "Pobočná odborová organizace a organizace zaměstnavatelů",
    "734": "Organizační jednotka zvláštní organizace pro zastoupení českých zájmů v mezinárodních nevládních organizacích",
    "736": "Pobočný spolek",
    "741": "Samosprávná stavovská organizace (profesní komora)",
    "745": "Komora (hospodářská, agrární)",
    "751": "Zájmové sdružení právnických osob",
    "761": "Honební společenstvo",
    "771": "Dobrovolný svazek obcí",
    "801": "Obec",
    "804": "Kraj",
    "805": "Regionální rada regionu soudržnosti",
    "811": "Městská část, městský obvod",
    "906": "Zahraniční spolek",
    "907": "Mezinárodní odborová organizace",
    "908": "Mezinárodní organizace zaměstnavatelů",
    "921": "Mezinárodní nevládní organizace",
    "922": "Organizační jednotka mezinárodní nevládní organizace",
    "931": "Evropské hospodářské zájmové sdružení",
    "932": "Evropská společnost",
    "933": "Evropská družstevní společnost",
    "936": "Zahraniční pobočný spolek",
    "937": "Pobočná mezinárodní odborová organizace",
    "938": "Pobočná mezinárodní organizace zaměstnavatelů",
    "941": "Evropské seskupení pro územní spolupráci",
    "960": "Právnická osoba zřízená zvláštním zákonem zapisovaná do veřejného rejstříku",
    "961": "Svěřenský fond",
    "962": "Zahraniční svěřenský fond"
}



@dataclass
class AresCompany:
    ico: str
    name: Optional[str]
    address: Optional[str]
    psc: Optional[str]
    legal_form: Optional[str]
    business_fields: Optional[List[str]]
    size: Optional[str]
    main_cz_nace: Optional[str] = None
    based_main_cz_nace: Optional[str] = None

def translate_legal_form(legal_form_code: str) -> str:
    # Vrátí textovou reprezentaci právní formy, pokud je kód známý, jinak vrátí původní kód
    return legal_forms.get(legal_form_code, legal_form_code)


def find_cznace_description(key, csv_path: str = "cznace.csv"):
    try:
        df = pd.read_csv(csv_path, delimiter=';', dtype={'id_cznace': str})
        description = df.loc[df['id_cznace'] == key, 'text_cznace'].values
        if len(description) > 0:
            return description[0]
        else:
            logging.info(f'Žádný popis pro id_cznace: {key} nebyl nalezen.')
            return None
    except Exception as e:
        logging.error(f'Chyba při načítání nebo vyhledávání v souboru {csv_path}: {e}')
        return None

def find_company_size(chodnota, csv_path: str = "pocet_pracovniku.csv"):
    try:
        df = pd.read_csv(csv_path, delimiter=',', dtype={'chodnota': str})
        size_text = df.loc[df['chodnota'] == chodnota, 'zkrtext'].values
        if len(size_text) > 0:
            return size_text[0]
        else:
            logging.info(f'Žádná velikost společnosti pro chodnota: {chodnota} nebyla nalezena.')
            return None
    except Exception as e:
        logging.error(f'Chyba při načítání nebo vyhledávání v souboru {csv_path}: {e}')
        return None



def new_get_company_data_ares(ico: str, redis_key_suffix:str = "_company_data_test") -> Optional[AresCompany]:
    redis_key = f"{ico}{redis_key_suffix}"

    # Zkusí najít data v Redisu
    cached_data = redis_instance.get(redis_key)
    if cached_data:
        logging.info("Data nalezena v Redisu.")
        # Deserializace dat z JSON stringu zpět do objektu AresCompany
        return AresCompany(**json.loads(cached_data))


    ares_url: str = f'https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty-res/{ico}'
    response = requests.get(ares_url, headers={'accept': 'application/json'})
    if response.status_code != 200:
        logging.error(f"Status code for request to {ares_url} is {response.status_code}")
        return None

    data = response.json()
    records = data.get("zaznamy", [])
    if not records:
        logging.error("Žádné záznamy.")
        return None

    record:dict = records[0]
    address_components = record.get('sidlo', {})
    address = address_components.get('textovaAdresa')
    psc = address_components.get('psc')
    business_field_codes = record.get('czNace', [])
    business_field_descriptions = [find_cznace_description(code) for code in business_field_codes if isinstance(find_cznace_description(code), str)]
    kategorie_poctu_pracovniku:str = record.get("statistickeUdaje").get("kategoriePoctuPracovniku")

    company_data = AresCompany(
        ico=record.get('ico'),
        name=record.get('obchodniJmeno'),
        address=address,
        psc=str(psc) if psc else None,
        legal_form=translate_legal_form(record.get('pravniForma')),
        business_fields=business_field_descriptions,
        size=find_company_size(kategorie_poctu_pracovniku)
    )

    # Serializace dat do JSON stringu a uložení do Redisu na 5 minut
    redis_instance.set(redis_key, json.dumps(company_data.__dict__), ex=60*5)

    return company_data



def main():
    something = new_get_company_data_ares("27405354")
    print(something)
    pass

if __name__ == "__main__":
    main()
