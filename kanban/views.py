from datetime import datetime
from functools import wraps
from uuid import uuid4

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select

from kanban.database import Session
from kanban.models import Card, CardCategory, User

from bcrypt import gensalt, hashpw

def required_fields(*fields):
    def decorator(function):
        @wraps(function)
        async def inner(request: Request, *args, **kwargs):
            body = await request.json()
            for field in fields:
                if body.get(field) is None:
                    raise HTTPException(status_code=400, detail=f'required field "{field}"')
            return await function(request, *args, **kwargs)
        return inner
    return decorator


def token_required(function):
    @wraps(function)
    async def decorator(request: Request, *args, **kwargs):
        with Session() as session:
            body = await request.json()
            if body.get('user_id') is None:
                raise HTTPException(status_code=400, detail='required field "user_id"')
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            if user is None:
                raise HTTPException(status_code=400, detail='invalid user_id')
            return await function(request, *args, **kwargs)
    return decorator


def init_app(app):
    @app.get('/user')
    @token_required
    async def get_user(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            return JSONResponse(user.to_dict())

    @app.post('/user')
    @required_fields('name', 'email', 'password')
    async def create_user(request: Request):
        with Session() as session:
            body = await request.json()
            salt = gensalt(8)
            password = hashpw(body['password'].encode('utf-8'), salt).decode('utf-8')
            user_uuid = str(uuid4())
            user = User(
                id=user_uuid,
                name=body['name'],
                email=body['email'],
                password=str(password),
                photo=body.get('photo'),
            )
            session.add(user)
            session.commit()
            session.flush()
            return JSONResponse(user.to_dict())

    @app.put('/user')
    @token_required
    @required_fields('name', 'password', 'email')
    async def update_user(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            salt = gensalt(8)
            password = hashpw(body['password'].encode('utf-8'), salt).decode('utf-8')
            user.name = body['name']
            user.password = password
            user.email = body['email']
            user.photo = body.get('photo')
            user.update_at = datetime.now()
            session.commit()
            session.flush()
            return JSONResponse(user.to_dict())

    @app.delete('/user')
    @token_required
    async def delete_user(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            session.delete(user)
            session.commit()
            session.flush()
            return JSONResponse(user.to_dict())

    @app.get('/card')
    @token_required
    async def get_cards(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            query = select(Card).where(Card.user_id == user.id)
            cards = [card.to_dict() for card in session.scalars(query).all()]
            return JSONResponse(cards)

    @app.get('/card/{card_id}')
    @token_required
    async def get_card(request: Request, card_id: str):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            card = session.get(Card, card_id)
            if card and card.user_id == user.id:
                return JSONResponse(card.to_dict())
            else:
                return JSONResponse({'error': 'card not found'}, status_code=404)

    @app.post('/card')
    @token_required
    @required_fields('title', 'category_id', 'status')
    async def create_card(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            category = session.get(CardCategory, body['category_id'])
            if category is None:
                return JSONResponse({'error': 'invalid category_id'}, status_code=400)
            card = Card(
                status=body['status'],
                title=body['title'],
                description=body.get('description'),
                category_id=category.id,
                id=str(uuid4()),
                user_id=user.id,
            )
            session.add(card)
            session.commit()
            session.flush()
            return JSONResponse(card.to_dict())

    @app.put('/card')
    @token_required
    @required_fields('id', 'status', 'title', 'category_id')
    async def update_card(request: Request):
        with Session() as session:
            body = await request.json()
            card = session.get(Card, body['id'])
            if card:
                card.status = body['status']
                card.title = body['title']
                card.description = body.get('description')
                card.update_at = datetime.now()
                card.category_id = body['category_id']
                session.commit()
                session.flush()
                return JSONResponse(card.to_dict())
            else:
                return JSONResponse({'error': 'card not found'}, status_code=404)

    @app.delete('/card')
    @token_required
    @required_fields('id')
    async def delete_card(request: Request):
        with Session() as session:
            body = await request.json()
            card = session.get(Card, body['id'])
            if card is None:
                return JSONResponse({'error': 'card not found'}, status_code=404)
            session.delete(card)
            session.commit()
            session.flush()
            return JSONResponse(card.to_dict())

    @app.get('/card-category')
    @token_required
    async def get_cards_categories(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            query = select(CardCategory).where(CardCategory.user_id == user.id)
            cards_categories = [
                card_category.to_dict()
                for card_category in session.scalars(query).all()
            ]
            return JSONResponse(cards_categories)

    @app.get('/card-category/{card_category_id}')
    @token_required
    async def get_card_category(request: Request, card_category_id: str):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            card_category = session.get(CardCategory, card_category_id)
            if card_category and card_category.user_id == user.id:
                return JSONResponse(card_category.to_dict())
            else:
                return JSONResponse({'error': 'card category not found'}, status_code=404)

    @app.post('/card-category')
    @token_required
    @required_fields('name', 'color')
    async def create_card_category(request: Request):
        with Session() as session:
            body = await request.json()
            query = select(User).where(User.id == body['user_id'])
            user = session.scalars(query).first()
            card_category = CardCategory(
                name=body['name'],
                color=body['color'], 
                user_id=user.id,
                id=str(uuid4())
            )
            session.add(card_category)
            session.commit()
            session.flush()
            return JSONResponse(card_category.to_dict())

    @app.put('/card-category')
    @token_required
    @required_fields('category_id', 'name', 'color')
    async def update_card_category(request: Request):
        with Session() as session:
            body = await request.json()
            card_category = session.get(CardCategory, body['category_id'])
            if card_category:
                card_category.name = body['name']
                card_category.color = body['color']
                card_category.update_at = datetime.now()
                session.commit()
                session.flush()
                return JSONResponse(card_category.to_dict())
            else:
                return JSONResponse({'error': 'card category not found'}, status_code=404)

    @app.delete('/card-category')
    @token_required
    @required_fields('category_id')
    async def delete_card_category(request: Request):
        with Session() as session:
            body = await request.json()
            card_category = session.get(CardCategory, body['category_id'])
            if card_category is None:
                return JSONResponse({'error': 'card category not found'}, status_code=404)
            session.delete(card_category)
            session.commit()
            session.flush()
            return JSONResponse(card_category.to_dict())