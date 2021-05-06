<template>
  <div ref="container" :style="{ 'width': width, 'height': height }">
    <svg ref="chart" style="width: 100%; height: 100%;" v-show="holes">
      <line class="bisector"
        :x1="xScale(0)" :x2="xScale(1)" :y1="yScale(0)" :y2="yScale(1)" />
      <line class="filtration-index"
        :x1="xScale(filtrationIndex)" :x2="xScale(filtrationIndex)" :y1="yScale(0)" :y2="yScale(filtrationIndex)" />
      <line class="filtration-index"
        :x1="xScale(0)" :x2="xScale(filtrationIndex)" :y1="yScale(filtrationIndex)" :y2="yScale(filtrationIndex)" />
      <g class="legend">
        <rect :x="xScale(0.65)" :y="yScale(0.35)"
          :width="xScale(0.90)-xScale(0.65)" :height="yScale(0.15)-yScale(0.35)" />
        <line class="persistence-line" :stroke="colorScale(0)"
          :x1="xScale(0.7)" :x2="xScale(0.75)" :y1="yScale(0.3)" :y2="yScale(0.3)" />
        <text :x="xScale(0.8)" :y="yScale(0.3)">H0</text>
        <line class="persistence-line" :stroke="colorScale(1)"
          :x1="xScale(0.7)" :x2="xScale(0.75)" :y1="yScale(0.2)" :y2="yScale(0.2)" />
        <text :x="xScale(0.8)" :y="yScale(0.2)">H1</text>
      </g>
      <line v-for="(hole, index) in extendedHoles" :key="index"
        class="persistence-line"
        :x1="xScale(hole.birth)" :x2="xScale(hole.birth)" :y1="yScale(hole.birth)" :y2="yScale(hole.death)"
        :stroke="colorScale(hole.dimension)" />
    </svg>
    <div class="d-flex justify-center align-center" style="width: 100%; height: 100%;" v-if="!holes">
      <v-progress-circular :size="70" :width="7" color="blue-grey" indeterminate />
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'

  export default {
    name: 'PersistenceDiagram',
    props: {
      holes: { type: Array },
      filtrationIndex: { type: Number, default: 0 },
      width: { type: String, default: "100%" },
      height: { type: String, default: "500px" },
    },
    data: function () {
      return {
        plotRange: [[0,1], [0,1]],
        isMounted: false,
      }
    },
    computed: {
      svg() {
        return d3.select(this.$refs.chart);
      },
      chartHeight() {
        if (this.isMounted) {
          return this.$refs.container.offsetHeight;
        } else return 0;
      },
      chartWidth() {
        if (this.isMounted) {
          return this.$refs.container.offsetWidth;
        } else return 0;
      },
      colorScale() {
        return d3.scaleOrdinal().domain([0,1]).range(d3.schemeDark2);
      },
      xScale() {
        return d3.scaleLinear().domain(this.plotRange[0]).range([50,this.chartWidth-30]);
      },
      yScale() {
        return d3.scaleLinear().domain(this.plotRange[1]).range([this.chartHeight-50,10]);
      },
      extendedHoles() {
        let _holes = [];
        this.holes.forEach(hole => {
          [hole.x1, hole.y1] = this.scalePoint([hole.birth, hole.birth]);
          [hole.x2, hole.y2] = this.scalePoint([hole.birth, hole.death]);
          _holes.push(hole)
        })
        return _holes;
      }
    },
    methods: {
      getRandomPoint() {
        let [[xMin, xMax], [yMin, yMax]] = this.plotRange;
        return [xMin+Math.random()*(xMax-xMin), yMin+Math.random()*(yMax-yMin)]
      },
      scalePoint([x, y]) {
        return [this.xScale(x), this.yScale(y)];
      },
    },
    mounted: function () {
      this.isMounted = true;
      let xAxis = d3.axisBottom()
        .scale(this.xScale)
        .ticks(10);
      let yAxis = d3.axisLeft()
        .scale(this.yScale)
        .ticks(10);
      this.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${this.yScale(0)})`)
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", "-.55em")
        .attr("transform", "rotate(-90)" );
      this.svg.append("g")
        .attr("class", "y axis")
        .attr("transform", `translate(${this.xScale(0)},0)`)
        .call(yAxis)
        .append("text")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Value ($)");
    }
  }
</script>

<style>
.persistence-line {
  stroke-width: 5;
  stroke-linecap: round;
}
.axe {
  stroke: black;
  stroke-width: 1;
  stroke-linejoin: round;
}
.bisector {
  stroke: gray;
  stroke-width: 1;
  stroke-linejoin: round;
  stroke-dasharray: 10 5;
  stroke-opacity: 0.2;
}
.filtration-index {
  stroke: red;
  stroke-width: 1;
  stroke-linejoin: round;
  stroke-dasharray: 10 5;
  stroke-opacity: 0.2;
}
.legend > text {
  fill: black;
  dominant-baseline: middle;
}
.legend > rect {
  fill: white;
  stroke: gray;
  stroke-width: 0.2;
}
</style>
