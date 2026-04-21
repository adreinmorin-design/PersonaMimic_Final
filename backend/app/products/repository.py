import asyncio

from sqlalchemy.orm import Session

from app.products.models import Product


class ProductRepository:
    """
    Studio Standard Repository for digital product management.
    Decouples product lifecycle logic from SQLAlchemy sessions.
    """

    async def get_product(self, db: Session, product_id: int) -> Product | None:
        return await asyncio.to_thread(self._get_product_sync, db, product_id)

    def _get_product_sync(self, db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.id == product_id).first()

    async def find_by_name(self, db: Session, product_name: str) -> Product | None:
        return await asyncio.to_thread(self._find_by_name_sync, db, product_name)

    def _find_by_name_sync(self, db: Session, product_name: str) -> Product | None:
        return (
            db.query(Product)
            .filter(Product.name == product_name)
            .order_by(Product.id.desc())
            .first()
        )

    async def find_fuzzy(self, db: Session, normalized_name: str) -> Product | None:
        return await asyncio.to_thread(self._find_fuzzy_sync, db, normalized_name)

    def _find_fuzzy_sync(self, db: Session, normalized_name: str) -> Product | None:
        all_products = db.query(Product).order_by(Product.created_at.desc()).all()
        for candidate in all_products:
            c_name = (candidate.name or "").strip().lower().replace(" ", "_")
            if c_name and (
                c_name == normalized_name or normalized_name in c_name or c_name in normalized_name
            ):
                return candidate
        return None

    async def list_all(self, db: Session) -> list[Product]:
        return await asyncio.to_thread(self._list_all_sync, db)

    def _list_all_sync(self, db: Session) -> list[Product]:
        return db.query(Product).order_by(Product.created_at.desc()).all()

    async def update_state(self, db: Session, product_name: str, **kwargs) -> Product:
        return await asyncio.to_thread(self._update_state_sync, db, product_name, **kwargs)

    def _update_state_sync(self, db: Session, product_name: str, **kwargs) -> Product:
        product = self._find_by_name_sync(db, product_name)
        if not product:
            product = Product(name=product_name)
            db.add(product)

        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product


product_repo = ProductRepository()
