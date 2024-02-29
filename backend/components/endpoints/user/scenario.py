from fastapi import APIRouter, Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas import business as BusinessSchemas
from components.services.account import AccountService
from components.services.business import BusinessService

router = APIRouter(prefix="/scenario")
