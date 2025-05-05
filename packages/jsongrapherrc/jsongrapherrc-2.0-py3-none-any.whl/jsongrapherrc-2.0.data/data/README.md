# JSONGrapherRC (JSONGrapher Record Creator)
A python package for creating JSONGrapher files which can then be plotted. 

To use JSONGrapherRC, first install it using pip:
<pre>
pip install JSONGrapherRC[COMPLETE]
</pre>

Alternatively, you can download the directory directly.<br> 

It is easiest to then follow the [example file](https://github.com/AdityaSavara/JSONGrapherRC/blob/main/example/exampleUsageJSONRecordCreator.py) to see how to create graphable .json records and to plot them. The .json files can then be dragged into www.jsongrapher.com<br>


## **1\. Preparing to Create a Record**

Let's create an example where we plot the height of a pear tree over several years. Assuming a pear tree grows approximately 0.40 meters per year, we'll generate sample data with some variation.
<pre>
x_label_including_units = "Time (years)"
y_label_including_units = "Height (m)"
time_in_years = [0, 1, 2, 3, 4]
tree_heights = [0, 0.42, 0.86, 1.19, 1.45]
</pre>

## **2\. Creating and Populating a New JSONGrapher Record**

<pre>
Record = JSONRecordCreator.create_new_JSONGrapherRecord()
Record.set_comments("Tree Growth Data collected from the US National Arboretum")
Record.set_datatype("Tree_Growth_Curve")
Record.set_x_axis_label_including_units(x_label_including_units)
Record.set_y_axis_label_including_units(y_label_including_units)
Record.add_data_series(series_name="pear tree growth", x_values=time_in_years, y_values=tree_heights, plot_type="scatter_spline")
Record.set_graph_title("Pear Tree Growth Versus Time")
</pre>

## **3\. Exporting to File**

We can export it to a .json file, which can then be used with JSONGrapher. 
<pre>
Record.export_to_json_file("ExampleFromTutorial.json")
Record.print_to_inspect()
</pre>

<p><strong>Expected Output:</strong></p>
<pre>
JSONGrapher Record exported to, ./ExampleFromTutorial.json
{
    "comments": "Tree Growth Data collected from the US National Arboretum",
    "datatype": "Tree_Growth_Curve",
    "data": [
        {
            "name": "pear tree growth",
            "x": [0, 1, 2, 3, 4],
            "y": [0, 0.42, 0.86, 1.19, 1.45],
            "type": "scatter",
            "line": { "shape": "spline" }
        }
    ],
    "layout": {
        "title": "Pear Tree Growth Versus Time",
        "xaxis": { "title": "Time (year)" },
        "yaxis": { "title": "Height (m)" }
    }
}
</pre>

## **4\. Plotting to Inspect**

We can also plot the data using Matplotlib and export the plot as a PNG file.
<pre>
Record.plot_with_matplotlib()
Record.export_to_matplotlib_png("ExampleFromTutorial_matplotlib_fig")
</pre>

And we can create an interactive graph with plotly:
<pre>
Record.plot_with_plotly() #Try hovering your mouse over points after this command!
</pre>

[![JSONGRapher record plotted using matplotlib](https://raw.githubusercontent.com/AdityaSavara/JSONGrapherRC/main/example/ExampleFromTutorial_matplotlib_fig.png)](https://raw.githubusercontent.com/AdityaSavara/JSONGrapherRC/main/example/ExampleFromTutorial_matplotlib_fig.png)