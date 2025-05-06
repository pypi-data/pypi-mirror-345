from sqlalchemy import create_engine


def test_sqla_create_engine():
    """
    Historically SQLalchemy's integration with this package has differed in behavior between Python versions. 
    This test should be run with each Python version that GX supports.
    """
    create_engine(
        "redshift+psycopg2://username:password@my-redshift-cluster.abcdef123456.us-west-2.redshift.amazonaws.com:5439/mydatabase"
    )
