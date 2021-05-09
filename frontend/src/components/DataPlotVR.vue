<template>
  <div>
    <div ref="container" :style="{ 'width': width, 'height': height }">
      <svg ref="chart" style="width: 100%; height: 100%;" v-show="points">
        <g class="markers" :visibility="this.showPoints?'visible':'hidden'">
          <circle v-for="(point, index) in points" :key="index"
            :cx="xScale(point[0])" :cy="yScale(point[1])" r="2" />
        </g>
        <g class="balls" :visibility="this.showBalls?'visible':'hidden'">
          <circle class="ball" v-for="(point, index) in points" :key="index"
            :cx="xScale(point[0])" :cy="yScale(point[1])" :r="ballsRadius" />
        </g>
        <g class="simplices" :visibility="this.showSimplices?'visible':'hidden'">
          <g class="d0simplices">
            <circle v-for="(simplex, index) in simplicesByDimension[0]" :key="index"
              :cx="xScale(simplex.points[0][0])" :cy="yScale(simplex.points[0][1])" :r="4"
              :opacity="simplex.value<filtrationIndex?1:0"/>
          </g>
          <g class="d1simplices">
            <line v-for="(simplex, index) in simplicesByDimension[1]" :key="index"
              :x1="xScale(simplex.points[0][0])" :y1="yScale(simplex.points[0][1])"
              :x2="xScale(simplex.points[1][0])" :y2="yScale(simplex.points[1][1])"
              :opacity="simplex.value<filtrationIndex?1:0"/>
          </g>
          <g class="d2simplices">
            <polygon v-for="(simplex, index) in simplicesByDimension[2]" :key="index"
              :points="`${xScale(simplex.points[0][0])},${yScale(simplex.points[0][1])} ${xScale(simplex.points[1][0])},${yScale(simplex.points[1][1])} ${xScale(simplex.points[2][0])},${yScale(simplex.points[2][1])}`"
              :opacity="simplex.value<filtrationIndex?1:0"/>
          </g>
        </g>
      </svg>
      <div class="d-flex justify-center align-center" style="width: 100%; height: 100%;" v-if="!points">
        <v-progress-circular :size="70" :width="7" color="blue-grey" indeterminate />
      </div>
    </div>
    <div class="my-3 d-flex justify-space-around">
      <v-switch v-model="showPoints" :label="$t('Show points')" hide-details></v-switch>
      <v-switch v-model="showBalls" :label="$t('Show balls')" hide-details></v-switch>
      <v-switch v-model="showSimplices" :label="$t('Show simplices')" hide-details></v-switch>
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'

  export default {
    name: 'DataPlot',
    props: {
      points: { type: Array },
      simplices: { type: Array },
      filtrationIndex: { type: Number, default: 0 },
      margin: { type: Number, default: 0.1 },
      width: { type: String, default: "100%" },
      height: { type: String, default: "700px" },
    },
    data: function () {
      return {
        showPoints: true,
        showBalls: true,
        showSimplices: true,
        isMounted: false,
      }
    },
    computed: {
      svg() {
        return d3.select(this.$refs.chart);
      },
      canvas() {
        return this.svg.append("g");
      },
      chartHeight() {
        if (this.isMounted) {
          return this.$refs.container.offsetHeight;
        } else return 600;
      },
      chartWidth() {
        if (this.isMounted) {
          return this.$refs.container.offsetWidth;
        } else return 100;
      },
      plotRange() {
        let transposedPoints = this.points[0].map((_, colIndex) => this.points.map(row => row[colIndex]));
        let [xMin, xMax] = [Math.min(...transposedPoints[0]), Math.max(...transposedPoints[0])];
        let [yMin, yMax] = [Math.min(...transposedPoints[1]), Math.max(...transposedPoints[1])];
        return [
          [xMin-this.margin*(xMax-xMin), xMax+this.margin*(xMax-xMin)],
          [yMin-this.margin*(yMax-yMin), yMax+this.margin*(yMax-yMin)],
        ]
      },
      xScale() {
        return d3.scaleLinear().domain(this.plotRange[0]).range([0, this.chartWidth]);
      },
      yScale() {
        return d3.scaleLinear().domain(this.plotRange[1]).range([0, this.chartWidth]);
      },
      ballsRadius() {
        return this.xScale(this.filtrationIndex) - this.xScale(0);
      },
      simplicesByDimension() {
        let simplicesByDimension = [[],[],[]];
        this.simplices.forEach((element) => {
          simplicesByDimension[element.dimension].push(element);
        });
        return simplicesByDimension;
      }
    },
    methods: {
      scalePoint([x, y]) {
        return [this.xScale(x), this.yScale(y)];
      },
      zoom: function () {
        this.canvas.attr("transform", `translate(${d3.event.transform.x}, ${d3.event.transform.y}) scale(${d3.event.transform.k})`);
      },
    },
    watch: { 
      filtrationIndex: function() {
        this.canvas.selectAll(".simplex").attr("opacity", d => (d.value < this.filtrationIndex)?1:0);
      },
      $refs: function() {
        this.chartHeight;
        this.chartWidth;
      }
    },
    mounted: function () {
      this.isMounted = true;
      this.svg.call(d3.zoom().on('zoom', this.zoom));
    }
  }
  </script>

<style>
  .markers {
    fill: blue;
  }
  .d0simplices {
    fill: purple;
  }
  .d1simplices {
    stroke: purple;
    stroke-width: 2;
    stroke-linejoin: round;
  }
  .d2simplices {
    fill: purple;
    opacity: 0.5;
  }
  .ball {
    fill: orange;
    opacity: 0.5;
  }
</style>
