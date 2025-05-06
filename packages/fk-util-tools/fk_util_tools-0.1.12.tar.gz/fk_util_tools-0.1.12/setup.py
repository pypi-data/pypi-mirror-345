from setuptools import setup, find_packages


VERSION = '0.1.12'
PACKAGE_NAME = 'fk_util_tools'
AUTHOR = 'Steven Santacruz Garcia'
AUTHOR_EMAIL = 'stevengarcia1118@gmail.com'
URL = 'https://gitlab.com/f3315/team-back-end/cross/packages/package_utils'

LICENSE = 'MIT'
DESCRIPTION = """Herramientas de utilidad o funciones comunes para los proyectos de FK."""
LONG_DESCRIPTION = DESCRIPTION
LONG_DESC_TYPE = 'text/markdown'

INSTALL_REQUIRES = [
    'boto3',
    'opentelemetry-api',
    'opentelemetry-sdk',
    'opentelemetry-instrumentation-fastapi',
    'opentelemetry-instrumentation-flask',
    'opentelemetry-instrumentation-django',
    'opentelemetry-exporter-otlp',
    'opentelemetry-instrumentation-sqlalchemy',
    'opentelemetry-instrumentation-requests',
    'opentelemetry-exporter-jaeger',
    'opentelemetry-instrumentation-psycopg2',
    'psycopg2-binary',
    'starlette'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)
