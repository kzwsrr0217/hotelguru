<template>
  <v-container>
    <h1 class="text-center mb-5">Grid Rendszer Teszt</h1>

    <v-row justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card outlined>
          <v-card-title>Teszt Kártya</v-card-title>
          <v-card-text>
            Ez a kártya egy v-col komponensben van.
            A szélességének változnia kellene a képernyő méretétől függően.
            <ul>
              <li>XS (alap): 12/12 szélesség</li>
              <li>SM (kis): 8/12 szélesség</li>
              <li>MD (közepes): 6/12 szélesség</li>
              <li>LG (nagy): 4/12 szélesség</li>
            </ul>
            Méretezd át a böngészőablakot a hatáshoz!
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-5">
      <v-col cols="12" md="8">
          <v-alert type="info" variant="outlined" density="compact">
              Ha a fenti "Teszt Kártya" helyesen átméreteződik, akkor a probléma valószínűleg
              a LoginView.vue specifikus CSS-ével vagy komplexebb belső struktúrájával van.
              Ha ez sem méreteződik át helyesen, akkor általánosabb probléma van a Vuetify
              grid rendszer betöltésével vagy alkalmazásával a projektben.
          </v-alert>
      </v-col>
    </v-row>

  </v-container>
</template>

<script setup>
// Nincs szükség script logikára ehhez a teszthez
</script>

<style scoped>
/* Itt lehetnek egyedi stílusok, ha szükségesek a teszthez */
.v-card {
  padding: 16px; /* Csak hogy legyen belső térköz */
  border: 2px dashed blue; /* Jól látható keret a teszthez */
}
ul {
    margin-top: 10px;
    padding-left: 20px;
}
</style>