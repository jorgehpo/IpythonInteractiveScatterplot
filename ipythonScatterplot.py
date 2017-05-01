from IPython.core.display import display, HTML
from string import Template
import pandas as pd
import os
import random

# load_d3 must be run once in ipython
def load_d3():
    display(HTML('<script src="lib/d3/d3.min.js"></script>'))


def read_svg(path):
    with open(path, 'r') as data:
        return (data.read())

def _draw_scatterplot(data, width, height):
    div_number = int(random.random()*100000)
    div_name = "scatterplot_div" + str(div_number)

    html_template = Template('''
        <div id="$div_name"></div>
        <script type="text/javascript"> $js_text </script>
        ''')

    template_js = Template("""
            function create_scatterplot(){
                let div_name = "#$div_name";
                let dot_radius = 2;
                let data = $data;
                let width = $width;
                let height = $height;

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
                    .range([dot_radius, width - dot_radius]);

                let yscale = d3.scale.linear()
                    .domain(d3.extent(data, (d)=>d.y ))
                    .range([dot_radius, height - dot_radius]);

                let circles = svg.selectAll("circle").data(data, function(obj){
                        //compute object id
                        return obj['id'];
                    });

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
                        return color_scale(data['label']);
                    });
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