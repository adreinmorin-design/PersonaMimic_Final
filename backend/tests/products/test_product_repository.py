from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.products.models import Product
from app.products.repository import ProductRepository


def _build_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


def test_find_fuzzy_matches_exact_partial_and_containing_names():
    db = _build_db_session()
    repo = ProductRepository()
    db.add_all(
        [
            Product(name="Whop Nexus"),
            Product(name="Whop"),
            Product(name="Another Product"),
        ]
    )
    db.commit()

    exact = repo._find_fuzzy_sync(db, "whop_nexus")
    assert exact is not None
    assert exact.name == "Whop Nexus"

    partial = repo._find_fuzzy_sync(db, "whop_nexus_engine")
    assert partial is not None
    assert partial.name == "Whop Nexus"

    broader = repo._find_fuzzy_sync(db, "whop")
    assert broader is not None
    assert broader.name in {"Whop Nexus", "Whop"}


def test_find_fuzzy_ignores_blank_input():
    db = _build_db_session()
    repo = ProductRepository()

    assert repo._find_fuzzy_sync(db, "") is None
