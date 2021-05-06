<template>
  <div>
    <div ref="container" :style="{ 'width': width, 'height': height }">
      <svg ref="chart" style="width: 100%; height: 100%;" v-show="points" />
      <div class="d-flex justify-center align-center" style="width: 100%; height: 100%;" v-if="!points">
        <v-progress-circular :size="70" :width="7" color="blue-grey" indeterminate />
      </div>
    </div>
    <div class="my-3 d-flex justify-space-around">
      <v-switch v-model="showPoints" :label="$t('Show points')" hide-details></v-switch>
      <v-switch v-model="showGrid" :label="$t('Show grid')" hide-details></v-switch>
      <v-switch v-model="showKde" :label="$t('Show KDE')" hide-details></v-switch>
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
      grid: { type: Array },
      simplices: { type: Array },
      margin: { type: Number, default: 0.1 },
      kdeData: { type: Array },
      filtrationIndex: { type: Number, default: 0 },
      width: { type: String, default: "100%" },
      height: { type: String, default: "700px" },
    },
    data: function () {
      return {
        showPoints: true,
        showGrid: false,
        showKde: true,
        showSimplices: true,
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
        return this.$refs.container.offsetHeight;
      },
      chartWidth() {
        return this.$refs.container.offsetWidth;
      },
      plotRange() {
        if (this.points.length == 0) {
          return [[0,1],[0,1]]
        }
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
        return d3.scaleLinear().domain(this.plotRange[1]).range([0, this.chartHeight]);
      },
    },
    methods: {
      scalePoint([x, y]) {
        return [this.xScale(x), this.yScale(y)];
      },
      drawPoints: function () {
        this.points.forEach((element) => {
          [element.x, element.y] = this.scalePoint(element);
        })
        this.canvas.append("g").attr("class", "markers").attr("visibility", this.showPoints?"visible":"hidden")
          .selectAll("circle")
          .data(this.points)
          .enter()
          .append("circle")
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)
          .attr("r", 2) 
      },
      drawGrid: function () {
        let [[xMin, xMax], [yMin, yMax]] = this.plotRange;
        let d3Grid = this.canvas.append('g').attr("class", "grid-lines").attr("visibility", this.showGrid?"visible":"hidden");
        d3Grid.selectAll("grid-line")
          .data(this.grid[0])
          .enter()
          .append("line")
          .attr("x1", d => this.xScale(d))
          .attr("x2", d => this.xScale(d))
          .attr("y1", this.yScale(yMin))
          .attr("y2", this.yScale(yMax));
        d3Grid.selectAll("grid-line")
          .data(this.grid[1])
          .enter()
          .append("line")
          .attr("x1", this.xScale(xMin))
          .attr("x2", this.xScale(xMax))
          .attr("y1", d => this.yScale(d))
          .attr("y2", d => this.yScale(d));
      },
      drawSimplices: function () {
        let simplicesByDimension = [[],[],[]];
        this.simplices.forEach((element) => {
          element.pointsCoordinates = element.points.map(this.scalePoint);
          simplicesByDimension[element.dimension].push(element);
        });
        let d3Simplices = this.canvas.append("g").attr("class", "simplices").attr("visibility", this.showSimplices?"visible":"hidden")
        d3Simplices.append("g").attr("class", "d0simplices")
          .selectAll("circle")
          .data(simplicesByDimension[0])
          .enter()
          .append("circle")
          .attr("class", "simplex")
          .attr("cx", d => d.pointsCoordinates[0][0])
          .attr("cy", d => d.pointsCoordinates[0][1])
          .attr("r", 4)
          .attr("opacity", d => (d.value < this.filtrationIndex)?1:0);
        d3Simplices.append("g").attr("class", "d1simplices")
          .selectAll("line")
          .data(simplicesByDimension[1])
          .enter()
          .append("line")
          .attr("class", "simplex")
          .attr("x1", d => d.pointsCoordinates[0][0])
          .attr("x2", d => d.pointsCoordinates[1][0])
          .attr("y1", d => d.pointsCoordinates[0][1])
          .attr("y2", d => d.pointsCoordinates[1][1])
          .attr("opacity", d => (d.value < this.filtrationIndex)?1:0);
        d3Simplices.append("g").attr("class", "d2simplices")
          .selectAll("rect")
          .data(simplicesByDimension[2])
          .enter()
          .append("rect")
          .attr("class", "simplex")
          .attr("x", d => d.pointsCoordinates[0][0])
          .attr("y", d => d.pointsCoordinates[0][1])
          .attr("width", d => d.pointsCoordinates[d.pointsCoordinates.length - 1][0] - d.pointsCoordinates[0][0])
          .attr("height", d => d.pointsCoordinates[d.pointsCoordinates.length - 1][1] - d.pointsCoordinates[0][1])
          .attr("opacity", d => (d.value < this.filtrationIndex)?1:0);
      },
      drawKde: function () {
        let kdeCells = [];
        let nRows = this.kdeData.length, nCols = this.kdeData[0].length;
        let [[xMin, xMax], [yMin, yMax]] = this.plotRange;
        let xPrecision = (xMax - xMin) / nCols, yPrecision = (yMax - yMin) / nRows;
        let [[xMin2, yMin2], [xMax2, yMax2]] = [this.scalePoint([xMin, yMin]),this.scalePoint([xMax,yMax])];
        let xPrecision2 = (xMax2-xMin2) / nCols, yPrecision2 = (yMax2-yMin2) / nCols;
        this.kdeData.forEach((row, i) => {
          row.forEach((col, j) => {
            let cell = {}
            cell.point = [xMin + j*xPrecision, yMin + i*yPrecision];
            cell.coordinates = this.scalePoint(cell.point);
            cell.value = col;
            kdeCells.push(cell);
          })
        });
        let allValues = Array.prototype.concat(...this.kdeData);
        let colorScale = d3.scaleLinear().domain([Math.min(...allValues),Math.max(...allValues)]).range([0, 1]);
        let d3Kde = this.canvas.append("g").attr("class", "kde").attr("visibility", this.showKde?"visible":"hidden");
        d3Kde.selectAll(".kde-cell")
          .data(kdeCells)
          .enter()
          .append("rect")
          .attr("class", "kde-cell")
          .attr("x", d => d.coordinates[0] - xPrecision2/2)
          .attr("y", d => d.coordinates[1] - yPrecision2/2)
          .attr("width", xPrecision2)
          .attr("height", yPrecision2)
          .attr("opacity", d => colorScale(d.value));
      },
      zoom: function () {
        this.canvas.attr("transform", `translate(${d3.event.transform.x}, ${d3.event.transform.y}) scale(${d3.event.transform.k})`);
      },
    },
    watch: { 
      points: function() {
        this.canvas.selectAll(".markers").remove();
        this.drawPoints();
      },
      grid: function() {
        this.canvas.selectAll(".grid-lines").remove();
        this.drawGrid();
        this.canvas.selectAll(".markers").remove();
        this.drawPoints();
      },
      simplices: function() {
        this.canvas.selectAll(".kde").remove();
        this.drawKde();
        this.canvas.selectAll(".simplices").remove();
        this.drawSimplices();
        this.canvas.selectAll(".markers").remove();
        this.drawPoints();
      },
      filtrationIndex: function() {
        this.canvas.selectAll(".simplex").attr("opacity", d => (d.value < this.filtrationIndex)?1:0);
      },
      showPoints: function() {
        this.canvas.selectAll(".markers").attr("visibility", this.showPoints?"visible":"hidden");
      },
      showGrid: function() {
        this.canvas.selectAll(".grid-lines").attr("visibility", this.showGrid?"visible":"hidden");
      },
      showSimplices: function() {
        this.canvas.selectAll(".simplices").attr("visibility", this.showSimplices?"visible":"hidden");
      },
      showKde: function() {
        this.canvas.selectAll(".kde").attr("visibility", this.showKde?"visible":"hidden");
      },
    },
    mounted: function () {
      this.svg.call(d3.zoom().on('zoom', this.zoom));
      this.drawKde();
      this.drawGrid();
      this.drawPoints();
      this.drawSimplices();
    }
  }
  </script>

<style>
  .grid-lines {
    stroke: gray;
    stroke-width: 1;
    stroke-linejoin: miter;
    stroke-dasharray: 10 5;
    stroke-opacity: 0.2;
  }
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
  .kde-cell {
    fill: orange;
  }
</style>
