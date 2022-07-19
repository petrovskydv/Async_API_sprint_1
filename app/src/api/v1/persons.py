from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import Person
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=Person, description='Информация о персоне')
async def genre_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return person


@router.get('/', response_model=list[Person], description='Список персон')
async def get_persons(
        person_service: PersonService = Depends(get_person_service),
):
    persons = []
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return persons
