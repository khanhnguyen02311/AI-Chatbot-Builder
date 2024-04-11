from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.schemas.business_field import ListBusinessFieldFULL
from components.repositories.business_field import BusinessFieldRepository

router = APIRouter()


@router.get("/business-fields")
async def get_business_field_list():
    with POSTGRES_SESSION_FACTORY() as session:
        repository = BusinessFieldRepository(session=session)
        business_fields = repository.get_all()
        return JSONResponse(content=ListBusinessFieldFULL.model_validate(business_fields).model_dump())
