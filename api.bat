call env/Scripts/activate
cd src
uvicorn api_module.api:app --reload