import logging


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if debug else logging.ERROR)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)
