# Dockerfile for hotelguru-frontend (Development)

# 1. Válasszunk egy hivatalos Node.js alap image-et
# Használhatsz egy specifikus verziót, ami megfelel a projekt igényeinek (pl. 16, 18, 20)
# Az 'alpine' verziók kisebbek, de néha kompatibilitási problémák lehetnek natív modulokkal
FROM node:18

# 2. Állítsuk be a munkakönyvtárat a konténeren belül
WORKDIR /app

# 3. Másoljuk be a package.json és (ha van) package-lock.json fájlokat
# Ez kihasználja a Docker réteg-gyorsítótárazását: ha ezek nem változnak,
# az npm install lépést nem kell újra futtatni image építéskor.
COPY package*.json ./

# 4. Telepítsük a függőségeket
# Fejlesztői környezetben általában az összes (dev) függőségre szükség van
# A --force kapcsoló néha segít verzióütközéseknél, de óvatosan használd.
# Ha yarn-t használsz: RUN yarn install
RUN npm install

# 5. Másoljuk be az alkalmazás többi kódját a munkakönyvtárba
# Megjegyzés: Mivel a docker-compose.yml volume-ot használ a kód csatolására ("/app"),
# ez a lépés főleg az image kezdeti állapotához és a cache-eléshez fontos.
# A futó konténer valójában a hostról csatolt kódot fogja látni és használni.
COPY . .

# 6. Tegyük elérhetővé a portot, amin a fejlesztői szerver futni fog (általában 3000)
# Ennek egyeznie kell a docker-compose.yml 'ports' beállításával (3000:3000)
EXPOSE 5173

# 7. Alapértelmezett parancs az alkalmazás (fejlesztői szerver) indítására
# Ez általában az 'npm start' a package.json scriptjei alapján.
# Ezt felül lehet bírálni a docker-compose.yml `command` direktívájával.
# Ha yarn-t használsz: CMD ["yarn", "start"]
CMD ["npm", "run", "dev", "--", "--host"]