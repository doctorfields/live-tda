<template>

<div style="height: 900px; width: 100%">
    <l-map
      :zoom="zoom"
      :center="center"
    >
      <l-tile-layer
        :url="url"
      />
      <l-marker v-if="source" :lat-lng="latLng(source.latitude, source.longitude)">
        <l-tooltip :options="{ permanent: true, interactive: true }">
          <strong>{{ source.city }}</strong>
          <div>{{ source.country }}</div>
          <small class="grey--text font-italic font-weight-light">Datacenter #{{ source.datacenter }}</small>
        </l-tooltip>
      </l-marker>
      <l-marker v-if="destiny" :lat-lng="latLng(destiny.latitude, destiny.longitude)">
        <l-tooltip :options="{ permanent: true, interactive: true }">
          <strong>{{ destiny.city }}</strong>
          <div>{{ destiny.country }}</div>
          <small class="grey--text font-italic font-weight-light">Datacenter #{{ destiny.datacenter }}</small>
        </l-tooltip>
      </l-marker>
      <template v-if="path">
        <l-polyline :lat-lngs="formatPolyline()" color="#8f34eb" :weight="2" dashArray="10,10" :opacity="0.5"></l-polyline>
        <l-marker v-for="pop in path.pops.slice(1, -1)" :key="pop.pop_id" :lat-lng="latLng(pop.latitude, pop.longitude)">
          <l-tooltip :options="{ permanent: true, interactive: true }">
            <strong>{{ pop.city }}</strong>
            <div>{{ pop.country }}</div>
            <small class="grey--text small font-italic font-weight-light">Datacenter #{{ pop.datacenter }}</small>
          </l-tooltip>
        </l-marker>
        <l-circle-marker v-for="bb in path.backbones" :key="bb.backbone_id"
          :lat-lng="getBackboneLatLng(bb)" :opacity="1" :radius="5" color="#8f34eb" :fillOpacity="1" fillColor="#8f34eb">
          <l-popup :options="{ permanent: true, interactive: true }">
            <strong>Latency: {{ bb.latency }}ms</strong>
            <div>Price: {{ bb.price }}€/Mb</div>
            <div>Active capacity: {{ bb.active_capacity }}</div>
            <div>Availale capacity: {{ bb.available_capacity }}</div>
          </l-popup>
        </l-circle-marker>
      </template>
    </l-map>
  </div>

</template>

<script>
  import { latLng } from "leaflet";
  import { LMap, LTileLayer, LMarker, LTooltip, LPolyline, LCircleMarker, LPopup } from "vue2-leaflet";

  export default {
    name: "Map",
    props: ["path", "source", "destiny", ],
    components: {
      LMap,
      LTileLayer,
      LMarker,
      LTooltip,
      LPolyline,
      LCircleMarker,
      LPopup
    },
    data() {
      return {
        zoom: 2.5,
        center: latLng(16.2, -25.6),
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        origZoom: 2.5,
        origCenter: latLng(16.2, -25.6),
        mapOptions: {
          zoomSnap: 0.5
        },
      };
    },
    methods: {
      latLng(latitude, longitude) {
        return latLng(latitude, longitude)
      },
      updateCenterAndZoom() {
        if (this.source && this.destiny) {
          let newLat = (parseFloat(this.source.latitude) + parseFloat(this.destiny.latitude)) / 2;
          let newLng = (parseFloat(this.source.longitude) + parseFloat(this.destiny.longitude)) / 2;
          this.center = this.latLng(newLat, newLng);
          this.zoom = this.origZoom;
        } else if (this.source) {
          let newLat = this.source.latitude;
          let newLng = this.source.longitude;
          this.center = this.latLng(newLat, newLng);
          this.zoom = this.origZoom;
        } else if (this.destiny) {
          let newLat = this.destiny.latitude;
          let newLng = this.destiny.longitude;
          this.center = this.latLng(newLat, newLng);
          this.zoom = this.origZoom;
        } else {
          this.center = this.origCenter;
          this.zoom = this.origZoom;
        }
      },
      formatPolyline() {
        if (!this.path) {
          return []
        } else {
          let latlngs = [];
          this.path.pops.forEach(pop => {
            latlngs.push([parseFloat(pop.latitude), parseFloat(pop.longitude)])
          })
          return latlngs
        }
      },
      getBackboneLatLng(backbone) {
        let srcLat = parseFloat(backbone.source.latitude);
        let srcLng = parseFloat(backbone.source.longitude);
        let dstLat = parseFloat(backbone.destiny.latitude);
        let dstLng = parseFloat(backbone.destiny.longitude);
        let srcLatRad = srcLat  * (Math.PI / 180);
        let dstLatRad = dstLat  * (Math.PI / 180);
        let middleLatRad = Math.atan(Math.sinh(Math.log(Math.sqrt(
          (Math.tan(dstLatRad)+1/Math.cos(dstLatRad))*(Math.tan(srcLatRad)+1/Math.cos(srcLatRad))))));
        let middleLat = middleLatRad * (180 / Math.PI)
        let middleLng = (srcLng + dstLng) / 2;
        return this.latLng(middleLat, middleLng);
      },
    },
    watch: {
      source: function (newValue, oldValue) {
        if (JSON.stringify(newValue) == JSON.stringify(oldValue)) {
          return
        }
        this.updateCenterAndZoom();
      },
      destiny: function (newValue, oldValue) {
        if (JSON.stringify(newValue) == JSON.stringify(oldValue)) {
          return
        }
        this.updateCenterAndZoom();
      },
    },
  };
</script>

<style>

</style>
