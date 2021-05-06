<template>
  <div ref="container" :style="{ 'width': width, 'height': height }">
    <apexchart ref="thisChart" type="area" :height="height" :options="options" :series="series" />
  </div>
</template>

<script>
  import apexchart from "vue-apexcharts";

  export default {
    name: "TimeSerierChart",
    components: {
      apexchart
    },
    props: {
      series: { 
        type: Array,
        defualt: [{
          "data": [],
        }],
      },
      width: {
        type: String,
        default: "100%",
      },
      height: {
        type: String,
        default: "200px",
      },
      options: {
        type: Object,
        default: function() {
          return {
            chart: {
              foreColor: "#999",
              stacked: true,
              dropShadow: {
                enabled: true,
                enabledSeries: [0],
                top: -2,
                left: 2,
                blur: 5,
                opacity: 0.06
              }
            },
            stroke: {
              curve: "smooth",
              width: 3
            },
            dataLabels: {
              enabled: false
            },
            markers: {
              size: 0,
              strokeColor: "#fff",
              strokeWidth: 3,
              strokeOpacity: 1,
              fillOpacity: 1,
              hover: {
                size: 6
              }
            },
            xaxis: {
              type: "datetime",
            },
            tooltip: {
              x: {
                format: "dd MMM yyyy"
              },
            },
          }
        },
      },
    },
  };
</script>

<style scoped></style>
