import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse

from ares import get_company_data_ares, AresCompany
from czso import czso_get_website_content, czso_parse_content, czso_get_base_cz_nace
from vat_new import VatInfo, Company
from verification import verify_ico

app = FastAPI()

logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)




@app.get("/", response_class=HTMLResponse)
def get_root(request: Request):
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        logging.info(f"Client IP: {client_ip}")
    else:
        logging.warning("X-Forwarded-For header not found")

    with open("index.html", "r") as file:
        return file.read()


@app.get(
    "/company/{company_ico}",
    description="Get company information by IČO.",
    response_model=AresCompany,
)
def get_company(company_ico: str):
    if verify_ico(company_ico):
        striped_company_ico = company_ico.strip()
        logging.info(f"Someone asked for IČO: {striped_company_ico}")
        company_data = get_company_data_ares(striped_company_ico)

        content = czso_get_website_content(striped_company_ico)
        parsed_content = czso_parse_content(content)
        if parsed_content:
            ares_main_economic_activity_cz_nace = str(parsed_content[0])
            ares_based_main_economic_activity_cz_nace = czso_get_base_cz_nace(
                ares_main_economic_activity_cz_nace
            )

            setattr(company_data, "main_cz_nace", ares_main_economic_activity_cz_nace)
            setattr(
                company_data,
                "based_main_cz_nace",
                ares_based_main_economic_activity_cz_nace,
            )

        json_data = jsonable_encoder(company_data)

        return json_data
    else:
        raise HTTPException(status_code=400, detail="Invalid ICO")


@app.get(
    "/companyVAT/{vat_number}",
    description="Get company information by VAT number.",
    response_model=Company
)
def get_vat_company(vat_number: str):
    striped_vat_ico = vat_number.strip()
    logging.info(f"Someone asked for VAT: {striped_vat_ico}")

    vat_info = VatInfo(striped_vat_ico)
    company = vat_info.get_vat_info()
    
    logging.info(company)
    #cached_info = company.get_cached_company_info()
    #if cached_info is not None:
    #    logging.info(f"Company info from cache: {cached_info}")
    #    return cached_info
    #else:
    #    html = company.get_company_info()
    #    company_info = CompanyByVAT.parse_company_info(html)
    #    
    #    if all(value == "" for value in company_info.values()):
    #        logging.info("Company info is empty, not caching.")
    #    else:
    #        company.cache_company_info(company_info)
    #        logging.info(f"Company info from web: {company_info}")


    if company.isValid:
        return company
    else:
        raise HTTPException(status_code=400, detail=company.userError)
