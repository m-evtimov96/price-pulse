from db.models import Category
from sqlalchemy.ext.asyncio import AsyncSession

NSI_CATEGORIES = [
    {"nsi_id": "01.1.1.1.00", "name": "Ориз"},
    {"nsi_id": "01.1.1.2.00", "name": "Брашно и други зърнени продукти"},
    {"nsi_id": "01.1.1.3.01", "name": "Хляб"},
    {"nsi_id": "01.1.1.3.02", "name": "Хляб \"Добруджа\""},
    {"nsi_id": "01.1.2.8.10", "name": "Кайма"},
    {"nsi_id": "01.1.4.0.0", "name": "Прясно мляко"}, 
    {"nsi_id": "01.1.4.4.00", "name": "Кисели млека"},
    {"nsi_id": "01.1.4.5.10", "name": "Сирене бяло саламурено"},
    {"nsi_id": "01.1.4.5.30", "name": "Кашкавал"},
    {"nsi_id": "01.1.4.7.00", "name": "Яйца и яйчни продукти"},
    {"nsi_id": "01.1.5.1.00", "name": "Млечни масла"},
    {"nsi_id": "01.1.5.2.00", "name": "Маргарин"},
    {"nsi_id": "01.1.5.4.00", "name": "Други течни растителни мазнини (олио)"},
    {"nsi_id": "01.1.7.3.01", "name": "Зрял боб"},
    {"nsi_id": "01.1.7.3.02", "name": "Леща"},
    {"nsi_id": "01.1.7.4.10", "name": "Картофи"},
    {"nsi_id": "01.1.8.1.00", "name": "Захар"},
    {"nsi_id": "01.1.8.3.02", "name": "Шоколад и шоколадови изделия"},
    {"nsi_id": "01.1.9.1.10", "name": "Оцет"},
    {"nsi_id": "01.1.9.2.10", "name": "Сол"},
    {"nsi_id": "01.2.1.1.00", "name": "Кафе"},
    {"nsi_id": "01.2.2.2.10", "name": "Газирани напитки"},
]

async def init_nsi_categories(session: AsyncSession):
    for cat in NSI_CATEGORIES:
        existing = await session.execute(
            Category.__table__.select().where(Category.nsi_id == cat["nsi_id"])
        )
        result = existing.first()
        if not result:
            session.add(Category(**cat))
    await session.commit()