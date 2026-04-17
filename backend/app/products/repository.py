from sqlalchemy.orm import Session

from app.products.models import Product


class ProductRepository:
    """
    Studio Standard Repository for digital product management.
    Decouples product lifecycle logic from SQLAlchemy sessions.
    """

    def get_product(self, db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.id == product_id).first()

    def find_by_name(self, db: Session, product_name: str) -> Product | None:
        return (
            db.query(Product)
            .filter(Product.name == product_name)
            .order_by(Product.id.desc())
            .first()
        )

    def find_fuzzy(self, db: Session, normalized_name: str) -> Product | None:
        """Ported from swarm_repo for cross-domain consistency."""
        all_products = db.query(Product).order_by(Product.created_at.desc()).all()
        for candidate in all_products:
            c_name = (candidate.name or "").strip().lower().replace(" ", "_")
            if c_name and (
                c_name == normalized_name or normalized_name in c_name or c_name in normalized_name
            ):
                return candidate
        return None

    def list_all(self, db: Session) -> list[Product]:
        return db.query(Product).order_by(Product.created_at.desc()).all()

    def update_state(self, db: Session, product_name: str, **kwargs) -> Product:
        product = self.find_by_name(db, product_name)
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
