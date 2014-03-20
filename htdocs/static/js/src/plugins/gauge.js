define(['libs/d3.v2'], function () {

    /*
     Gauge implementation in D3. Heavily inspired by JustGage - http://justgage.com/

     TODO: Scale fonts based on radius
     TODO: Proper inner shadow on both arcs.

     */

    function JohnGauge(config) {
        var nodeId = config.nodeId,
            radius = config.radius || 100,
            width = 2 * radius,
            ir = radius * 0.6,
            pi = Math.PI,
            min = config.min || 0,
            max = config.max || 100,
            value = config.value || 0,
            thresholds = config.thresholds || [];

        this.notation = config.notation || '\u00B0';  // Default is degrees
        this.animationSpeed = 1000;  // Speed of value transitions

        /* Create SVG element */
        var vis = d3.select("#" + nodeId).append('svg')
            .attr("width", width)
            .attr("height", radius)
            .append("svg:g")
            .attr("transform", "translate(" + radius + "," + radius + ")");
        this.vis = vis;

        /* Create linear scale for start and end points */
        this.myScale = d3.scale.linear().domain([min, max]).range([-90 * (pi/180), 90 * (pi/180)]);

        /* Create linear scale for color transitions */
        this.color = this.createColorScale(min, max, thresholds);

        /* Define arc */
        this.arc = d3.svg.arc().outerRadius(radius).innerRadius(ir).startAngle(this.myScale(min));

        /* Create background arc with gradient */
        var gradientId = this.createGradient(nodeId);
        vis.append('path')
            .datum({ endAngle: this.myScale(max)})
            .attr('d', this.arc)
            .attr('fill', 'url(#' + gradientId + ')');

        /* Create value arc */
        this.valueArc = vis.append('path')
            .datum({endAngle: this.myScale(min)})
            .attr('fill', this.color(min))
            .attr('opacity', '0.9')
            .attr('d', this.arc);

        /* Draw text elements */
        this.valueText = this.createTexts(ir, min, max);

        /* Draw thresholds */
        this.drawThresholds(thresholds);

        /* Initialize gauge with given value */
        this.refresh(value);
    }

    JohnGauge.prototype = {
        refresh: function (value) {
            var self = this;

            /* Transition arc and color to new value */
            this.valueArc.transition().duration(this.animationSpeed).call(arcTween, value)
                .transition().duration(this.animationSpeed).attr('fill', this.color(value));
            this.valueText.text(value + this.notation);

            function arcTween(transition, newValue) {
                /* Calculates end angles while transitioning */
                transition.attrTween('d', function (d) {
                    var interpolate = d3.interpolate(d.endAngle, self.myScale(newValue));
                    return function (t) {
                        d.endAngle = interpolate(t);
                        return self.arc(d);
                    };
                });
            }

        },
        createTexts: function (ir, min, max) {
            /* Create text that displays value */
            var valueText = this.vis.append('text')
                .text(min + this.notation)
                .attr('font-family', 'Arial')
                .attr('y', -ir/2 + 12.5)
                .attr('font-size', '25px')
                .attr('fill', 'black')
                .attr('font-weight', 'bold')
                .attr('text-anchor', 'middle'),

            /* Create text displaying min value */
                minText = this.vis.append('text')
                .text(min)
                .attr('font-family', 'Arial')
                .attr('fill', '#b3b3b3')
                .attr('font-size', '14px')
                .attr('y', '0')
                .attr('x', 5 - ir)
                .attr('text-anchor', 'start'),

            /* Create text displaying max value */
                maxText = this.vis.append('text')
                .text(max)
                .attr('font-family', 'Arial')
                .attr('fill', '#b3b3b3')
                .attr('font-size', '14px')
                .attr('y', '0')
                .attr('x', ir - 5)
                .attr('text-anchor', 'end');

            return valueText;
        },
        createColorScale: function (min, max, thresholds) {
            if (thresholds.length === 1) {
                max = thresholds[0];
            }
            return d3.scale.linear()
                .domain([min, (max - min) / 2, max])
                .interpolate(d3.interpolateRgb)
                .range(["#a9d70b", "#f9c802", "#ff0000"]);
        },
        createGradient: function (nodeId) {
            /* Greate gradient for background arc */
            var gradientId = nodeId + 'gradient';
            var grads = this.vis.append("defs")
                .append("radialGradient")
                .attr("gradientUnits", "userSpaceOnUse")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", "100%")
                .attr("id", gradientId);
            grads.append("stop").attr("offset", "10%").style("stop-color", "gainsboro");
            grads.append("stop").attr("offset", "50%").style("stop-color", "#edebeb");
            grads.append("stop").attr("offset", "90%").style("stop-color", "gainsboro");

            return gradientId;
        },
        drawThresholds: function (thresholds) {
            for (var i = 0, l = thresholds.length; i < l; i++) {
                this.createLineFromValue(thresholds[i]);
            }
        },
        createLineFromValue: function (value) {
            var points = this.getLineCoords(value);
            this.vis.append("line")
                .attr('stroke-width', 1).attr('stroke', 'black')
                .attr("x1", points.x1).attr("y1", points.y1)
                .attr("x2", points.x2).attr("y2", points.y2);
        },
        getLineCoords: function (value) {
            /* Get x and y coordinates for a specific value */
            var path = this.arc({ endAngle: this.myScale(value)}),
                defs = path.split(' '),
                lineCoords = defs[3].split('A')[0].split('L'),
                startPoint = lineCoords[0].split(','),
                endPoint = lineCoords[1].split(',');

            return { x1: startPoint[0], y1: startPoint[1], x2: endPoint[0], y2: endPoint[1]};
        }
    };


    return JohnGauge;

});