FROM python:3.13-slim

LABEL org.opencontainers.image.source=https://github.com/ssciwr/mondey-frontend-prototype
LABEL org.opencontainers.image.description="MONDEY backend production image"

WORKDIR /app

COPY . .

RUN pip install .

CMD ["mondey-backend"]
