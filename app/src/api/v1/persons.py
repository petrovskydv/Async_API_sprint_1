from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import PersonSchema
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=PersonSchema, description='Информация о персоне')
async def genre_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonSchema:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return PersonSchema(**person.dict())


@router.get('/', response_model=list[PersonSchema], description='Список персон')
async def get_persons(
        person_service: PersonService = Depends(get_person_service),
) -> list[PersonSchema]:
    persons = []
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return persons
