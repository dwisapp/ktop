FROM odoo:17.0

USER root

RUN pip3 install PyJWT

USER odoo
