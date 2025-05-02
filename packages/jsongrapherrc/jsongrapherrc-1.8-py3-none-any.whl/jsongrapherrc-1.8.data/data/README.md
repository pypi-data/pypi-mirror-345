# JSONGrapherRC
A python package for creating JSONGrapher Records

To use JSONGrapherRC, first install it using pip:
<pre>
pip install JSONGrapherRC[COMPLETE]
</pre>

Alternatively, you can download the directory directly.<br> 
It is easiest to then follow the [example file](https://github.com/AdityaSavara/JSONGrapherRC/blob/main/example/exampleUsageJSONRecordCreator.py) to learn.<br>


## **1\. Preparing to Create a Record**

Let's create an example where we plot the height of a pear tree over several years. Assuming a pear tree grows approximately 0.40 meters per year, we'll generate sample data with some variation.
<pre>
x_label_including_units = "Time (years)"
y_label_including_units = "Height (m)"
time_in_years = [0, 1, 2, 3, 4]
tree_heights = [0, 0.42, 0.86, 1.19, 1.45]
</pre>

## **2\. Creating and Populating a New JSONGrapher Record**

The easiest way to start is with the `create_new_JSONGrapherRecord()` function. While you *can* instantiate the JSONGrapherRecord class directly, this function is generally more convenient. We'll create a record and inspect its default fields.
<pre>
try:
    from JSONGRapherRC import JSONRecordCreator  # Normal usage
except ImportError:
    import JSONRecordCreator  # If the class file is local

Record = JSONRecordCreator.create_new_JSONGrapherRecord()
Record.set_comments("Tree Growth Data collected from the US National Arboretum")
Record.set_datatype("Tree_Growth_Curve")
Record.set_x_axis_label_including_units(x_label_including_units)
Record.set_y_axis_label_including_units(y_label_including_units)
Record.add_data_series(series_name="pear tree growth", x_values=time_in_years, y_values=tree_heights, plot_type="scatter_spline")
Record.set_graph_title("Pear Tree Growth Versus Time")
</pre>

## **3\. Exporting to File**

We now have a JSONGrapher record! We can export it to a file, which can then be used with JSONGrapher. 
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


We can also plot the data using Matplotlib and export the plot as a PNG file.
<pre>
Record.plot_with_matplotlib()
Record.export_to_matplotlib_png("ExampleFromTutorial")
</pre>

And we can create an interactive graph in a browser with plotly:
<pre>
Record.plot_with_plotly() #Try hovering the mouse over points in plotly figures!
</pre>

[![JSONGRapher record plotted using matplotlib](https://raw.githubusercontent.com/AdityaSavara/JSONGrapherRC/main/example/ExampleFromTutorial.png)](https://raw.githubusercontent.com/AdityaSavara/JSONGrapherRC/main/example/ExampleFromTutorial.png)