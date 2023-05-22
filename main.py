import logging
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse

from ares import get_company_data_ares, AresCompany
from czso import czso_get_website_content, czso_parse_content, czso_get_base_cz_nace


app = FastAPI()

logging.basicConfig(
    format='[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

@app.get("/", response_class=HTMLResponse)
def get_root():
    with open("index.html", "r") as file:
        logging.info("Someone hit the site")
        return file.read()





@app.get("/company/{company_ico}", description="Get company information by IČO.", response_model=AresCompany)
def get_company(company_ico: int):
    logging.info(f"Someone asked for IČO: {company_ico}")
    company_data = get_company_data_ares(str(company_ico).strip())
    
    content = czso_get_website_content(company_ico)
    parsed_content = czso_parse_content(content)
    
    if parsed_content:
        ares_main_economic_activity_cz_nace = czso_get_base_cz_nace(str(parsed_content[0]))
        setattr(company_data, "czso_get_base_cz_nace", ares_main_economic_activity_cz_nace)
        
    json_data = jsonable_encoder(company_data)
    
    return json_data
