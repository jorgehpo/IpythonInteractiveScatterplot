from IPython.core.display import display, HTML
from string import Template
import pandas as pd
import os
import random

# load_d3 must be run once in ipython
def load_d3():
    display(HTML('<script src="lib/d3/d3.min.js"></script>'))

def read_svg(path):
#    def remove_escapes(string):
#        escapes = ''.join([chr(char) for char in range(1, 32)])
#        return string.translate(None, escapes)
#    with open(path, 'r') as data:
#        return remove_escapes(data.read())
    with open(path, 'r') as data:
        return data.read()

def _draw_scatterplot(data, width, height):
    div_number = int(random.random()*100000)
    div_name = "scatterplot_div" + str(div_number)

    html_template = Template('''
        <style>
        body {
          font: 11px sans-serif;
        }

        .axis path,
        .axis line {
          fill: none;
          stroke: #000;
          shape-rendering: crispEdges;
        }

        .dot {
          stroke: #000;
        }
        </style>
        <div id="$div_name"></div>
        <script type="text/javascript"> $js_text </script>
        ''')

    template_js = Template("""
            function create_scatterplot(){
                let div_name = "#$div_name";
                let dot_radius = 4;
                let data = $data;
                let width = $width;
                let height = $height;

                let margin = {left: 30, right: 10, top: 10, bottom: 30}

                let svg = d3.select(div_name).append("svg").attr("width",width).attr("height",height);

                let clicked_div = d3.select(div_name).append("div").attr("id","clicked_div");

                let tooltip = d3.select(div_name).append("div")
                    .attr("id","tooltip$div_name")
                    .style("width", 200 + "px")
                    .style("height", 200 + "px")
                    .style("background-color", "#fff")
                    .style("position", "fixed")
                    .style("visibility", "hidden")
                    .style("border", "2px solid gray")
                    .style("border-radius", "5px");

                let color_scale = d3.scale.category10();

                let xscale = d3.scale.linear()
                    .domain(d3.extent(data, (d)=>d.x ))
                    .range([margin.left, width - margin.right]);

                let yscale = d3.scale.linear()
                    .domain(d3.extent(data, (d)=>d.y ))
                    .range([height - margin.bottom, margin.top]);

                let xAxis = d3.svg.axis().scale(xscale).orient("bottom");
                let yAxis = d3.svg.axis().scale(yscale).orient("left");

                let circles = svg.selectAll("circle").data(data);

                //Enter
                circles.enter().append("circle").attr("r", dot_radius).on("mouseover", function(x){
                    let coordinates = [d3.event.pageX, d3.event.pageY]; 
                    tooltip.style("visibility","visible")
                        .style("left", (coordinates[0] + 10) + "px")
                        .style("top", (coordinates[1] + 10) + "px");
                    tooltip.html(x['image']);
                })
                .on("mousemove", function(x){
                    let coordinates = [d3.event.pageX, d3.event.pageY]; 
                    tooltip.style("left", (coordinates[0] + 10) + "px")
                        .style("top", (coordinates[1] + 10) + "px")
                })
                .on("mouseout", function(x){
                    tooltip.style("visibility","hidden")
                })
                .on("click",function(x){
                    clicked_div.html("Clicked: "+x['id']);
                })


                //Exit
                circles.exit().remove();

                // Update
                circles
                    .attr("cx", function(data){
                        return (xscale(data['x']));
                    })
                    .attr("cy", function(data){
                        return (yscale(data['y']));
                    })
                    .style("fill", function(data){
                        return "#ffffff00";
                    })
                    .style("stroke", function(data){
                        return color_scale(data['label']);
                    })
                    .style("stroke-width", 1);

                svg.append("g")
                  .attr("class", "x axis")
                  .attr("transform", "translate(0," + (height - margin.bottom) + ")")
                  .call(xAxis)

                svg.append("g")
                  .attr("class", "y axis")
                  .attr("transform", "translate(" + (margin.left) + ", 0)")
                  .call(yAxis)

                // adding legends
                let legendDiv = d3.select(div_name).append("div").style("display","flex");
                
                let legend = legendDiv
                    .selectAll(".legend")
                    .data(color_scale.domain())
                    .enter()
                    .append("div")
                    .style("display", "flex")
                    .style("margin-left", "10px");

                let legendBox = legend.append("div")
                    .style("width", "20px")
                    .style("height", "20px")
                    .style("background-color", x => color_scale(x));

                let legendText = legend.append("div")
                    .style("height", "20px")
                    .style("margin-left", "5px")
                    .text(x => x);
            }
            create_scatterplot();
        """);

    js_text = template_js.substitute({"data":data, "div_name":div_name, "width":width, "height":height})
    
    html = html_template.substitute({"div_name":div_name, "js_text":js_text})    
    display(HTML(html))

# function to draw interactive scatterplot in jupyter (ipython) notebook
def interactive_scatterplot(x, y, ids, label_colors, img_dir, width = 500, height = 500):
    # Parameters:
    # x: x position of the points
    # y: y position of the points
    # ids: unique ids of the points. For each unique id, there must be an image with name [id].svg in the directory [img_dir]
    # label_colors: labels of each dot. Dot will be colored according to the label given example: "label1", "label2" ...
    # img_dir: directory containing one svg for each dot
    # width: width of the plot
    # height: height of the plot
    image_paths = [os.path.join(img_dir,idx) + ".svg" for idx in ids]
    images = [read_svg(img) for img in image_paths]
    df = pd.DataFrame({'x':x , 'y':y , 'id':ids, 'label':label_colors, 'image':images})
    data_json = df.to_dict(orient='records')
    _draw_scatterplot(data_json, width, height)



def interactive_scatterplot_svgs(x, y, ids, svgs, label_colors, width, height):
    df = pd.DataFrame({'x':x , 'y':y , 'id':ids, 'label':label_colors, 'image':svgs})
    data_json = df.to_dict(orient='records')
    _draw_scatterplot(data_json, width, height)
