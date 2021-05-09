<template>
  <v-app @keyup.enter="() => filtrationIndex += 0.01">
    <v-app-bar flat app>
        <v-img alt="LiveTDA" class="shrink mr-2" contain src="@/assets/logo.png" transition="scale-transition" width="40"/>
        <v-toolbar-title class="px-3">
            <span class="font-weight-light font-italic">Live</span>
            <span>TDA</span>
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
            <Languages/>
        </v-toolbar-items>
    </v-app-bar> 
    <v-content>
      <v-row class="mx-1">
        <v-col cols="12" sm="3">
          <v-card class="mx-1 my-3">
            <v-card-title>{{ $t('Data parameters') }}</v-card-title>
            <v-card-text>
              <v-radio-group v-model="dataOrigin" :label="$t('Data origin')" row>
                <v-radio :label="$t('Syntetic')" :value="'syntetic'"></v-radio>
                <v-radio :label="$t('From CSV file')" :value="'csv'"></v-radio>
              </v-radio-group>
              <v-slide-y-transition>
                <div v-show="dataOrigin == 'syntetic'">
                  <v-select v-model="shape" :items="shapeTypes" :label="$t('Cloud shape')" />
                  <div class="d-flex justify-space-between">
                    <v-text-field class="mx-1" v-model="N" type="number" :min="5" :label="$t('Number of points')" />
                    <v-text-field class="mx-1" v-model="error" type="number" :min="0" step="0.1" :label="$t('Error')" />
                    <v-text-field class="mx-1" v-model="seed" type="number" :label="$t('Random seed')" />
                  </div>
                </div>
              </v-slide-y-transition>
              <v-slide-y-transition>
                <div v-show="dataOrigin == 'csv'">
                  <v-file-input
                    accept="text/csv"
                    label="CSV file"
                  ></v-file-input>
                </div>
              </v-slide-y-transition>
            </v-card-text>
          </v-card>
          <v-card class="mx-1 my-3">
            <v-card-title>{{ $t('Filtration parameters') }}</v-card-title>
            <v-card-text>
              <v-select v-model="filtrationType" :items="filtrationTypes" :label="$t('Filtration type')" />
              <v-slide-y-transition>
                <div v-show="filtrationType == 'kde'">
                  <div class="d-flex justify-space-between">
                    <v-text-field class="mx-1" v-model="precision" type="number" :label="$t('Precision')" />
                    <v-text-field class="mx-1" v-model="margin" type="number" step="0.1" :label="$t('Margin')" />
                  </div>
                  <div class="d-flex justify-space-between">
                    <v-text-field class="mx-1" v-model="kdePrecision" type="number" :label="$t('KDE Precision')" :hint="$t('This only affects to visualization')"/>
                    <v-text-field class="mx-1" v-model="kdeBandwidth" type="number" step="0.1" :label="$t('KDE Bandwidth')" clearable />
                  </div>
                </div>
              </v-slide-y-transition>
              <v-slide-y-transition>
                <div v-show="filtrationType == 'vr'">
                  <div class="d-flex justify-space-between">
                    <v-text-field class="mx-1" v-model="margin" type="number" step="0.1" :label="$t('Margin')" :hint="$t('This only affects to visualization')"/>
                  </div>
                </div>
              </v-slide-y-transition>
              <v-slide-y-transition>
                <div v-show="filtrationType == 'cech'">
                  <div class="d-flex justify-space-between">
                    <v-text-field class="mx-1" v-model="margin" type="number" step="0.1" :label="$t('Margin')" :hint="$t('This only affects to visualization')"/>
                  </div>
                </div>
              </v-slide-y-transition>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card class="mx-1 my-3">
            <v-card-title>{{ $t('Filtration index') }}</v-card-title>
            <v-card-text>
              <v-slider v-model="filtrationIndex"
                :min="filtrationRange[0]" :max="filtrationRange[1]" :step="filtrationIndexStep"
                thumb-label
                tick-size=0.1
                :tick-labels="filtrationTickLabels"
              ></v-slider>
            </v-card-text>
          </v-card>
          <v-card class="mx-1 my-3">
            <v-card-title>{{ $t('Persistence diagram') }}</v-card-title>
            <v-card-text>
              <PersistenceDiagram :holes="holes" :filtrationRange="filtrationRange" :filtrationIndex="filtrationIndex" />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="5">
          <v-card class="mx-1 my-3">
            <v-card-title>{{ $t('Data cloud') }}</v-card-title>
            <v-card-text>
              <DataPlotKDE v-if="filtrationType=='kde'" :points="points" :margin="margin" :grid="grid" :simplices="filtrationSimplices" :kdeData="kdeData" :filtrationIndex="filtrationIndex" />
              <DataPlotVR v-if="filtrationType=='vr'" :points="points" :margin="margin" :simplices="filtrationSimplices" :filtrationIndex="filtrationIndex" />
              <DataPlotVR v-if="filtrationType=='cech'" :points="points" :margin="margin" :simplices="filtrationSimplices" :filtrationIndex="filtrationIndex" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-content>
    <Alert />
  </v-app>
</template>

<script>
  import requestsMixin from './helpers/requestsMixin'
  import Alert from './components/Alert'
  import Languages from './components/Languages'
  import DataPlotKDE from './components/DataPlotKDE'
  import DataPlotVR from './components/DataPlotVR'
  import PersistenceDiagram from './components/PersistenceDiagram'

  export default {
    name: 'App',
    mixins: [ requestsMixin, ],
    components: {
      Alert,
      Languages,
      DataPlotKDE,
      DataPlotVR,
      PersistenceDiagram,
    },
    data: () => {
      return {
        N: 20,
        error: 0.1,
        shape: "s1",
        seed: 42,
        precision: 20,
        margin: 0.5,
        kdePrecision: 100,
        kdeBandwidth: null,
        dataOrigin: "syntetic",
        points: [],
        grid: [[-1,1],[-1,1]],
        filtrationRange: [0,1],
        filtrationSimplices: [],
        holes: [],
        kdeData: [[]],
        filtrationType: "kde",
        filtrationIndex: 0,
        filtrationIndexStep: 0.01,
      }
    },
    computed: {
      dataFormSet() {
        return {
          shape: this.shape,
          N: this.N,
          error: this.error,
          seed: this.seed,
        }
      },
      filtrationFormSet() {
        return {
          type: this.filtrationType,
          points: this.points,
          precision: this.precision,
          margin: this.margin,
          kde_precision: this.kdePrecision,
          kde_bw: this.kdeBandwidth,
          max_distance: this.maxDistance,
        }
      },
      shapeTypes() {
        return [
          { value: "s1", text: this.$t("Circle") },
          { value: "s1vs1", text: this.$t("Two circles") },
        ]
      },
      filtrationTypes() {
        return [
          { value: "cech", text: this.$t("Ĉech") },
          { value: "vr", text: this.$t("Vietoris-Rips") },
          { value: "kde", text: this.$t("Cubical through KDE") },
        ]
      },
      filtrationTickLabels() {
        let nTicks = parseInt((this.filtrationRange[1]-this.filtrationRange[0]) / this.filtrationIndexStep);
        return [...Array(nTicks).keys()].map(x => (x%25==0)?x/100:null)
      },
    },
    methods: {
      getData() {
        if (this.N > 2) {
          this.request('get', 'generate-data/', {
            params: this.dataFormSet,
          }).then((response) => {
            this.points = response.data.points;
          })
        }
      },
      getHomology() {
        if (this.filtrationType == "kde") {
          this.request('post', 'get-cubical-homology/', {
            data: this.filtrationFormSet,
          }).then((response) => {
            this.grid = response.data.grid;
            this.filtrationSimplices = response.data.filtration.simplices;
            this.filtrationRange = response.data.filtration.range;
            this.holes = response.data.holes;
            this.kdeData = response.data.kde;
          })
        } else if (this.filtrationType == "vr") {
          this.request('post', 'get-vr-homology/', {
            data: this.filtrationFormSet,
          }).then((response) => {
            this.filtrationSimplices = response.data.filtration.simplices;
            this.filtrationRange = response.data.filtration.range;
            this.holes = response.data.holes;
          })
        } else if (this.filtrationType == "cech") {
          this.request('post', 'get-cech-homology/', {
            data: this.filtrationFormSet,
          }).then((response) => {
            this.filtrationSimplices = response.data.filtration.simplices;
            this.filtrationRange = response.data.filtration.range;
            this.holes = response.data.holes;
          })
        }
      },
    },
    mounted: function() {
      window.addEventListener('keydown', (e) => {
        if (e.key == 'ArrowLeft') {
          this.filtrationIndex -= this.filtrationIndexStep;
        } else if (e.key == 'ArrowRight') {
          this.filtrationIndex += this.filtrationIndexStep;
        }  
      });
      this.getData();
    },
    watch: {
      dataFormSet: function (newValue, oldValue) {
        if (JSON.stringify(newValue) == JSON.stringify(oldValue)) {
          return
        }
        this.getData();
      },
      filtrationFormSet: function (newValue, oldValue) {
        if (JSON.stringify(newValue) == JSON.stringify(oldValue)) {
          return
        }
        this.getHomology();
      },
    },
  };
</script>

<style scoped></style>
