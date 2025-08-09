from db.models import Category
from sqlalchemy.ext.asyncio import AsyncSession

NSI_CATEGORIES = [
    {"nsi_id": "01.1.1.1.00", "name": "Ориз"},
    {"nsi_id": "01.1.1.2.00", "name": "Брашно"},
    {"nsi_id": "01.1.1.3.01", "name": "Хляб"},
    {"nsi_id": "01.1.2.2.01", "name": "Свинско месо"},
    {"nsi_id": "01.1.2.4.01", "name": "Mесо от домашни птици"},
    {"nsi_id": "01.1.2.7.02", "name": "Малотрайни колбаси"},
    {"nsi_id": "01.1.2.7.03", "name": "Трайни колбаси"},
    {"nsi_id": "01.1.2.8.10", "name": "Кайма"},
    {"nsi_id": "01.1.4.1.00", "name": "Прясно мляко"}, 
    {"nsi_id": "01.1.4.4.00", "name": "Кисело мляко"},
    {"nsi_id": "01.1.4.5.10", "name": "Сирене"},
    {"nsi_id": "01.1.4.5.30", "name": "Кашкавал"},
    {"nsi_id": "01.1.4.7.00", "name": "Яйца"},
    {"nsi_id": "01.1.5.1.00", "name": "Масло"},
    {"nsi_id": "01.1.5.4.00", "name": "Олио"},
    {"nsi_id": "01.1.6.1.05", "name": "Цитрусови"},
    {"nsi_id": "01.1.6.1.06", "name": "Други пресни и замразени плодове"},
    {"nsi_id": "01.1.7.1.10", "name": "Домати"},
    {"nsi_id": "01.1.7.1.15", "name": "Краставици"},
    {"nsi_id": "01.1.7.1.25", "name": "Пипер"},
    {"nsi_id": "01.1.7.1.55", "name": "Други пресни зеленчуци"},
    {"nsi_id": "01.1.7.3.01", "name": "Боб"},
    {"nsi_id": "01.1.7.3.02", "name": "Леща"},
    {"nsi_id": "01.1.7.4.10", "name": "Картофи"},
    {"nsi_id": "01.1.8.1.00", "name": "Захар"},
    {"nsi_id": "01.1.8.3.02", "name": "Шоколад"},
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