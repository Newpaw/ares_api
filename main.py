import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path

from ares import get_company_data_ares, AresCompany
from helper import get_better_formated_domain
from czso import czso_get_website_content, czso_parse_content, czso_get_base_cz_nace
from vat_new import VatInfo, Company
from verification import verify_ico, verify_vat
from brandfetch_info import get_logo, get_logo_path, convert_svg_to_png

app = FastAPI()

logging.basicConfig(
    format="[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def raise_http_400_error(detail: str):
    raise HTTPException(status_code=400, detail=detail)


def check_for_spaces(input_string: str, error_message: str):
    if input_string != input_string.strip():
        raise_http_400_error(error_message)


@app.get("/", response_class=HTMLResponse)
def get_root(request: Request):
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        logging.info(f"Client IP: {client_ip}")
    else:
        logging.warning("X-Forwarded-For header not found")

    index_file = Path("index.html").read_text()
    return index_file


@app.get(
    "/company/{company_ico}",
    description="Get company information by IČO.",
    response_model=AresCompany,
)
def get_company(company_ico: str):
    check_for_spaces(company_ico, "IČ number should not contain spaces.")

    if not verify_ico(company_ico):
        raise_http_400_error("Invalid ICO")

    logging.info(f"Someone asked for IČO: {company_ico}")
    company_data = get_company_data_ares(company_ico.strip())

    content = czso_get_website_content(company_ico.strip())
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

    return jsonable_encoder(company_data)


@app.get(
    "/companyVAT/{vat_number}",
    description="Get company information by VAT number.",
    response_model=Company,
)
def get_vat_company(vat_number: str):
    check_for_spaces(vat_number, "VAT number should not contain spaces.")

    if not verify_vat(vat_number):
        raise_http_400_error("Invalid VAT number based on library pyvat.")

    vat_info = VatInfo(vat_number.strip())
    company = vat_info.get_vat_info()

    if company is None:
        raise_http_400_error("Company doesn´t exist.")

    if not company.isValid:
        raise_http_400_error(company.userError)

    return company


@app.get("/logo/{domain}", response_class=FileResponse, tags=["logo"], description="Download and save a company logo by domain.")
def get_company_logo(domain: str):
    domain_better_formated = get_better_formated_domain(domain.lower())
    get_logo(domain_better_formated)

    logo_path = get_logo_path(domain_better_formated)

    if logo_path:
        if logo_path.lower().endswith('.svg'):
            logo_path = convert_svg_to_png(logo_path)
        return FileResponse(logo_path, media_type='image/png')

    raise HTTPException(status_code=404, detail="Logo not found")
