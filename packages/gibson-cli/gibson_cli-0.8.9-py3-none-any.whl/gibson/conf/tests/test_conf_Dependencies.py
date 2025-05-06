from gibson.conf.Dependencies import Dependencies


def test_compute():
    dependencies = Dependencies().compute()

    assert dependencies.api == "fastapi==0.85"
    assert dependencies.model == "sqlalchemy==1.4"
    assert dependencies.revision == "alembic==1.12"
    assert dependencies.schema == "pydantic==2.6"
    assert dependencies.test == "pytest==7.1"
