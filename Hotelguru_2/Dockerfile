# Használjunk egy hivatalos Python 3.9 image-et Debian Linux alappal
FROM python:3.9-slim

# Környezeti változók
ENV PYTHONDONTWRITEBYTECODE 1 # Ne generáljon .pyc fájlokat
ENV PYTHONUNBUFFERED 1       # Python output azonnal jelenjen meg a logban

# Rendszerfüggőségek telepítése (Debian/Ubuntu alapú)
# Frissítjük a csomaglistát, telepítjük a WeasyPrint függőségeit és egyéb szükségeseket
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       # WeasyPrint függőségek:
       libpango-1.0-0 \
       libcairo2 \
       libpangocairo-1.0-0 \
       libgdk-pixbuf2.0-0 \
       shared-mime-info \
       libffi-dev \
    # Takarítás a telepítés után a méret csökkentése érdekében
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Állítsuk be a munkakönyvtárat a konténeren belül
WORKDIR /app

# Másoljuk be a Python függőségi listát
COPY requirements.txt .

# Telepítsük a Python függőségeket
# --no-cache-dir csökkenti az image méretét
RUN pip install --no-cache-dir -r requirements.txt

# Hozzunk létre egy mappát az adatbázis kötetnek
RUN mkdir /app/database

# Másoljuk be az alkalmazás teljes kódját a munkakönyvtárba
COPY . .

# Expose-oljuk a portot, amin a Flask futni fog
EXPOSE 8888

# Parancs az alkalmazás indítására
# Flask fejlesztői szervert használunk, de Gunicorn vagy Waitress jobb lenne élesben
# A --host=0.0.0.0 szükséges, hogy kívülről is elérhető legyen a konténer
# A FLASK_APP környezeti változót is beállítjuk (vagy használhatnánk `flask --app app run ...`)
ENV FLASK_APP=run_app:create_app()
CMD ["flask", "run", "--host=0.0.0.0", "--port=8888"]