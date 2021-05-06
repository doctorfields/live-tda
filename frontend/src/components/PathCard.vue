<template>
  <v-card width="250" height="700" class="ma-3" :color="active ? 'primary lighten-5' : 'white'" @click="toggle">
    <v-img height="70" src="@/assets/latency1.jpg">
      <v-card-title class="white--text">
        {{ $t("Latency") }}: {{ path.total_latency }}ms
      </v-card-title>
    </v-img>
      <v-card-text style="height: 575px; overflow-y: auto;">
        <v-timeline align-top dense>
          <v-timeline-item color="blue" small>
            <div>
              <strong>{{ path.backbones[0].source.city }}</strong>
              <div>{{ path.backbones[0].source.country }}</div>
            </div>
          </v-timeline-item>
          <v-timeline-item color="blue" small v-for="edge in path.backbones" :key="edge.backbone_id">
            <div>
              <strong>{{ edge.destiny.city }}</strong>
              <div>{{ edge.destiny.country }}</div>
              <div class="grey--text font-italic font-weight-light">{{ edge.latency }}ms - {{ edge.price }}€/Mb</div>
              <div class="grey--text font-italic font-weight-light"></div>
            </div>
          </v-timeline-item>
        </v-timeline>
      </v-card-text>
    <v-divider></v-divider>
    <v-card-actions class="justify-center">
      <v-chip color="orange" outlined>
        {{ $t("Total price") }}: {{ path.total_price }}€/Mb
      </v-chip>
    </v-card-actions>
  </v-card>
</template>

<script>
  export default {
    name: 'PathCard',
    props: ["path", "active"],
  }
</script>

<style scoped></style>
