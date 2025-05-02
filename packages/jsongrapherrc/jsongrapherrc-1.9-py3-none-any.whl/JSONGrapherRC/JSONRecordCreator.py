import json
#TODO: put an option to suppress warnings from JSONRecordCreator



#the function create_new_JSONGrapherRecord is intended to be "like" a wrapper function for people who find it more
# intuitive to create class objects that way, this variable is actually just a reference 
# so that we don't have to map the arguments.
def create_new_JSONGrapherRecord(hints=False):
    #we will create a new record. While we could populate it with the init,
    #we will use the functions since it makes thsi function a bit easier to follow.
    new_record = JSONGrapherRecord()
    if hints == True:
        new_record.add_hints()
    return new_record


class JSONGrapherRecord:
    """
    This class enables making JSONGrapher records. Each instance represents a structured JSON record for a graph.
    One can optionally provide an existing JSONGrapher record during creation to pre-populate the object.

    Arguments & Attributes (all are optional):
        comments (str): Can be used to put in general description or metadata related to the entire record. Can include citation links. Goes into the record's top level comments field.
        datatype: The datatype is the experiment type or similar, it is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. This ends up being the datatype field of the full JSONGrapher file. Avoid using double underscores '__' in this field  unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field, rather than a dataype name.
        graph_title: Title of the graph or the dataset being represented.
        data_objects_list (list): List of data series dictionaries to pre-populate the record. 
        x_data: Single series x data in a list or array-like structure. 
        y_data: Single series y data in a list or array-like structure.
        x_axis_label_including_units: A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units .
        y_axis_label_including_units: A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units .
        layout: A dictionary defining the layout of the graph, including axis titles,
                comments, and general formatting options.
    
    Methods:
        add_data_series: Adds a new data series to the record.
        set_layout: Updates the layout configuration for the graph.
        export_to_json_file: Saves the entire record (comments, datatype, data, layout) as a JSON file.
        populate_from_existing_record: Populates the attributes from an existing JSONGrapher record.
    """
    
    def __init__(self, comments="", graph_title="", datatype="", data_objects_list = None, x_data=None, y_data=None, x_axis_label_including_units="", y_axis_label_including_units ="", plot_type ="", layout={}, existing_JSONGrapher_record=None):
        """
        Initialize a JSONGrapherRecord instance with optional attributes or an existing record.

            layout (dict): Layout dictionary to pre-populate the graph configuration.
            existing_JSONGrapher_record (dict): Existing JSONGrapher record to populate the instance.
        """
        # Default attributes for a new record.
        # Initialize the main record dictionary
        # the if statements check if something is empty and populates them if not. This is a special syntax in python that does not require a None object to work, empty also works.
        
        #if receiving a data_objects_list, validate it.
        if data_objects_list:
            validate_plotly_data_list(data_objects_list) #call a function from outside the class.
        #if receiving axis labels, validate them.
        if x_axis_label_including_units:
            validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=False)
        if y_axis_label_including_units:
            validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=False)

        self.fig_dict = {
            "comments": comments,  # Top-level comments
            "datatype": datatype,  # Top-level datatype (datatype)
            "data": data_objects_list if data_objects_list else [],  # Data series list
            "layout": layout if layout else {
                "title": {"text": graph_title},
                "xaxis": {"title": {"text": x_axis_label_including_units}},
                "yaxis": {"title": {"text": y_axis_label_including_units}}
            }
        }

        self.plot_type = plot_type #the plot_type is normally actually a series level attribute. However, if somebody sets the plot_type at the record level, then we will use that plot_type for all of the individual series.
        if plot_type != "":
            self.fig_dict["plot_type"] = plot_type

        # Populate attributes if an existing JSONGrapher record is provided.
        if existing_JSONGrapher_record:
            self.populate_from_existing_record(existing_JSONGrapher_record)

        # Initialize the hints dictionary, for use later, since the actual locations in the JSONRecord can be non-intuitive.
        self.hints_dictionary = {}
        # Adding hints. Here, the keys are the full field locations within the record.
        self.hints_dictionary["['comments']"] = "Use Record.set_comments() to populate this field. Can be used to put in a general description or metadata related to the entire record. Can include citations and links. Goes into the record's top level comments field."
        self.hints_dictionary["['datatype']"] = "Use Record.set_datatype() to populate this field. This is the datatype, like experiment type, and is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. Avoid using double underscores '__' in this field  unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field, rather than a dataype name."
        self.hints_dictionary["['layout']['title']['text']"] = "Use Record.set_graph_title() to populate this field. This is the title for the graph."
        self.hints_dictionary["['layout']['xaxis']['title']['text']"] = "Use Record.set_x_axis_label() to populate this field. This is the x axis label and should have units in parentheses. The units can include multiplication '*', division '/' and parentheses '( )'. Scientific and imperial units are recommended. Custom units can be contained in pointy brackets'< >'."  # x-axis label
        self.hints_dictionary["['layout']['yaxis']['title']['text']"] = "Use Record.set_y_axis_label() to populate this field. This is the y axis label and should have units in parentheses. The units can include multiplication '*', division '/' and parentheses '( )'. Scientific and imperial units are recommended. Custom units can be contained in pointy brackets'< >'."


    #this function enables printing the current record.
    def __str__(self):
        """
        Returns a JSON-formatted string of the record with an indent of 4.
        """
        print("Warning: Printing directly will return the raw record without some automatic updates. It is recommended to use the syntax RecordObject.print_to_inspect() which will make automatic consistency updates and validation checks to the record before printing.")
        return json.dumps(self.fig_dict, indent=4)


    def add_data_series(self, series_name, x_values=[], y_values=[], simulate={}, comments="", plot_type="",  uid="", line="", extra_fields=None):
        """
        This is the normal way of adding an x,y data series.
        """
        # series_name: Name of the data series.
        # x: List of x-axis values. Or similar structure.
        # y: List of y-axis values. Or similar structure.
        # simulate: This is an optional field which, if used, is a JSON object with entries for calling external simulation scripts.
        # comments: Optional description of the data series.
        # plot_type: Type of the data (e.g., scatter, line).
        # line: Dictionary describing line properties (e.g., shape, width).
        # uid: Optional unique identifier for the series (e.g., a DOI).
        # extra_fields: Dictionary containing additional fields to add to the series.
        x_values = list(x_values)
        y_values = list(y_values)

        data_series_dict = {
            "name": series_name,
            "x": x_values, 
            "y": y_values,
        }

        #Add optional inputs.
        if len(comments) > 0:
            data_series_dict["comments"]: comments
        if len(uid) > 0:
            data_series_dict["uid"]: uid
        if len(line) > 0:
            data_series_dict["line"]: line
        #add simulate field if included.
        if simulate:
            data_series_dict["simulate"] = simulate
        # Add extra fields if provided, they will be added.
        if extra_fields:
            data_series_dict.update(extra_fields)
        #Add to the class object's data list.
        self.fig_dict["data"].append(data_series_dict)
        #update plot_type, since our internal function requires the data series to be added already.
        if len(plot_type) > 0:
            newest_record_index = len(self.fig_dict["data"]) - 1
            self.set_plot_type_one_data_series(newest_record_index, plot_type)

    #this function returns the current record.
    def get_record(self):
        """
        Returns a JSON-dict string of the record
        """
        return self.fig_dict

    def print_to_inspect(self, update_and_validate=True, validate=True, remove_remaining_hints=False):
        if remove_remaining_hints == True:
            self.remove_hints()
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        elif validate: #this will validate without doing automatic updates.
            self.validate_JSONGrapher_record()
        print(json.dumps(self.fig_dict, indent=4))

    def populate_from_existing_record(self, existing_JSONGrapher_record):
        """
        Populates attributes from an existing JSONGrapher record.
        existing_JSONGrapher_record: A dictionary representing an existing JSONGrapher record.
        """
        if "comments" in existing_JSONGrapher_record:   self.fig_dict["comments"] = existing_JSONGrapher_record["comments"]
        if "datatype" in existing_JSONGrapher_record:      self.fig_dict["datatype"] = existing_JSONGrapher_record["datatype"]
        if "data" in existing_JSONGrapher_record:       self.fig_dict["data"] = existing_JSONGrapher_record["data"]
        if "layout" in existing_JSONGrapher_record:     self.fig_dict["layout"] = existing_JSONGrapher_record["layout"]

    def import_from_dict(self, fig_dict):
        self.fig_dict = fig_dict
    
    #the json object can be a filename string or can be json object which is actually a dictionary.
    def import_from_json(self, json_filename_or_object):
        if type(json_filename_or_object) == type(""): #assume it's a filename and path.
            # Open the file in read mode
            with open("json_filename_or_object", 'r') as file:
                # Read the entire content of the file
                content = file.read()
                self.fig_dict = json.loads(content)   
        else:
            self.fig_dict = json_filename_or_object

    def set_plot_type_one_data_series(self, data_series_index, plot_type):
        data_series_dict = self.fig_dict['data'][data_series_index]
        data_series_dict = set_data_series_dict_plot_type(data_series_dict=data_series_dict, plot_type=plot_type)
        #now put the data_series_dict back:
        self.fig_dict['data'][data_series_index] = data_series_dict

    def set_plot_type_all_series(self, plot_type):
        """
        Sets the plot_type field for the all data series.
        options are: scatter, spline, scatter_spline
        """
        self.plot_type = plot_type
        for data_series_index in range(len(self.fig_dict['data'])): #works with array indexing.
            self.set_plot_type_one_data_series(data_series_index, plot_type)
     
       
    def update_plot_types(self, plot_type=None):
        """
        updates the plot types for every existing data series.
        
        """        
        #If optional argument not provided, take class instance setting.
        if plot_type == None: 
            plot_type = self.plot_type
        #If the plot_type is not blank, use it for all series.
        if plot_type != "":
            self.set_plot_type_all_series(plot_type)
        else: #if the plot_type is blank, then we will go through each data series and update them individually.
            for data_series_index, data_series_dict in enumerate(self.fig_dict['data']):
                #This will update the data_series_dict as needed, putting a plot_type if there is not one.
                data_series_dict = set_data_series_dict_plot_type(data_series_dict=data_series_dict)
                self.fig_dict['data'][data_series_index] = data_series_dict
 
    def set_datatype(self, datatype):
        """
        Sets the datatype field used as the experiment type or schema identifier.
            datatype (str): The new data type to set.
        """
        self.fig_dict['datatype'] = datatype

    def set_comments(self, comments):
        """
        Updates the comments field for the record.
            str: The updated comments value.
        """
        self.fig_dict['comments'] = comments

    def set_graph_title(self, graph_title):
        """
        Updates the title of the graph in the layout dictionary.
        graph_title (str): The new title to set for the graph.
        """
        self.fig_dict['layout']['title']['text'] = graph_title

    def set_x_axis_label_including_units(self, x_axis_label_including_units, remove_plural_units=True):
        """
        Updates the title of the x-axis in the layout dictionary.
        xaxis_title (str): The new title to set for the x-axis.
        """
        if "xaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("xaxis"), dict):
            self.fig_dict['layout']["xaxis"] = {}  # Initialize x-axis as a dictionary if it doesn't exist.
        validation_result, warnings_list, x_axis_label_including_units = validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["xaxis"]["title"]['text'] = x_axis_label_including_units

    def set_y_axis_label_including_units(self, y_axis_label_including_units, remove_plural_units=True):
        """
        Updates the title of the y-axis in the layout dictionary.
        yaxis_title (str): The new title to set for the y-axis.
        """
        if "yaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("yaxis"), dict):
            self.fig_dict['layout']["yaxis"] = {}  # Initialize y-axis as a dictionary if it doesn't exist.
        
        validation_result, warnings_list, y_axis_label_including_units = validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["yaxis"]["title"]['text'] = y_axis_label_including_units
    def set_x_axis_range(self, min, max):
        self.fig_dict["layout"]["xaxis"][0] = min
        self.fig_dict["layout"]["xaxis"][1] = max
    def set_y_axis_range(self, min, max):
        self.fig_dict["layout"]["yaxis"][0] = min
        self.fig_dict["layout"]["yaxis"][1] = max
        
    def set_layout(self, comments="", graph_title="", x_axis_label_including_units="", y_axis_label_including_units="", x_axis_comments="",y_axis_comments="", remove_plural_units=True):
        # comments: General comments about the layout. Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        # graph_title: Title of the graph.
        # xaxis_title: Title of the x-axis, including units.
        # xaxis_comments: Comments related to the x-axis.  Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        # yaxis_title: Title of the y-axis, including units.
        # yaxis_comments: Comments related to the y-axis.  Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        
        validation_result, warnings_list, x_axis_label_including_units = validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=remove_plural_units)              
        validation_result, warnings_list, y_axis_label_including_units = validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["title"]['text'] = graph_title
        self.fig_dict['layout']["xaxis"]["title"]['text'] = x_axis_label_including_units
        self.fig_dict['layout']["yaxis"]["title"]['text'] = y_axis_label_including_units
        

        #populate any optional fields, if provided:
        if len(comments) > 0:
            self.fig_dict['layout']["comments"] = comments
        if len(x_axis_comments) > 0:
            self.fig_dict['layout']["xaxis"]["comments"] = x_axis_comments
        if len(y_axis_comments) > 0:
            self.fig_dict['layout']["yaxis"]["comments"] = y_axis_comments     


        return self.fig_dict['layout']
    
    #This function validates the output before exporting, and also has an option of removing hints.
    def export_to_json_file(self, filename, update_and_validate=True, validate=True, remove_remaining_hints=False):
        """
        writes the json to a file
        returns the json as a dictionary.
        optionally removes hints before export and return.
        """
        if remove_remaining_hints == True:
            self.remove_hints()
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        elif validate: #this will validate without doing automatic updates.
            self.validate_JSONGrapher_record()

        # filepath: Optional, filename with path to save the JSON file.       
        if len(filename) > 0: #this means we will be writing to file.
            # Check if the filename has an extension and append `.json` if not
            if '.json' not in filename.lower():
                filename += ".json"
            #Write to file.
            with open(filename, 'w') as f:
                json.dump(self.fig_dict, f, indent=4)
        return self.fig_dict

    def get_plotly_fig(self, update_and_validate=True):
        import plotly.io as pio
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        fig = pio.from_json(json.dumps(self.fig_dict))
        return fig

    def plot_with_plotly(self, update_and_validate=True):
        fig = self.get_plotly_fig(update_and_validate=update_and_validate)
        fig.show()
        #No need for fig.close() for plotly figures.


    def export_to_plotly_png(self, filename, update_and_validate=True, timeout=10):
        fig = self.get_plotly_fig(update_and_validate=update_and_validate)       
        # Save the figure to a file, but use the timeout version.
        self.export_plotly_image_with_timeout(plotly_fig = fig, filename=filename, timeout=timeout)

    def export_plotly_image_with_timeout(self, plotly_fig, filename, timeout=10):
        # Ensure filename ends with .png
        if not filename.lower().endswith(".png"):
            filename += ".png"
        import plotly.io as pio
        pio.kaleido.scope.mathjax = None
        fig = plotly_fig
        
        def export():
            try:
                fig.write_image(filename, engine="kaleido")
            except Exception as e:
                print(f"Export failed: {e}")

        import threading
        thread = threading.Thread(target=export, daemon=True)  # Daemon ensures cleanup
        thread.start()
        thread.join(timeout=timeout)  # Wait up to 10 seconds
        if thread.is_alive():
            print("Skipping Plotly png export: Operation timed out. Plotly image export often does not work from Python. Consider using export_to_matplotlib_png.")

    def get_matplotlib_fig(self, update_and_validate=True):
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        fig = convert_JSONGrapher_dict_to_matplotlib_fig(self.fig_dict)
        return fig

    def plot_with_matplotlib(self, update_and_validate=True):
        import matplotlib.pyplot as plt
        fig = self.get_matplotlib_fig(update_and_validate=update_and_validate)
        plt.show()
        plt.close(fig) #remove fig from memory.

    def export_to_matplotlib_png(self, filename, update_and_validate=True):
        import matplotlib.pyplot as plt
        # Ensure filename ends with .png
        if not filename.lower().endswith(".png"):
            filename += ".png"
        fig = self.get_matplotlib_fig(update_and_validate=update_and_validate)       
        # Save the figure to a file
        fig.savefig(filename)
        plt.close(fig) #remove fig from memory.

    def add_hints(self):
        """
        Adds hints to fields that are currently empty strings using self.hints_dictionary.
        Dynamically parses hint keys (e.g., "['layout']['xaxis']['title']") to access and update fields in self.fig_dict.
        The hints_dictionary is first populated during creation of the class object in __init__.
        """
        for hint_key, hint_text in self.hints_dictionary.items():
            # Parse the hint_key into a list of keys representing the path in the record.
            # For example, if hint_key is "['layout']['xaxis']['title']",
            # then record_path_as_list will be ['layout', 'xaxis', 'title'].
            record_path_as_list = hint_key.strip("[]").replace("'", "").split("][")
            record_path_length = len(record_path_as_list)
            # Start at the top-level record dictionary.
            current_field = self.fig_dict

            # Loop over each key in the path.
            # For example, with record_path_as_list = ['layout', 'xaxis', 'title']:
            #    at nesting_level 0, current_path_key will be "layout";
            #    at nesting_level 1, current_path_key will be "xaxis";  <-- (this is the "xaxis" example)
            #    at nesting_level 2, current_path_key will be "title".
            # Enumerate over keys starting with index 1.
            for nesting_level, current_path_key in enumerate(record_path_as_list, start=1):
                # If not the final depth key, then retrieve from deeper.
                if nesting_level != record_path_length:
                    current_field = current_field.setdefault(current_path_key, {}) # `setdefault` will fill with the second argument if the requested field does not exist.
                else:
                    # Final key: if the field is empty, set it to hint_text.
                    if current_field.get(current_path_key, "") == "": # `get` will return the second argument if the requested field does not exist.
                        current_field[current_path_key] = hint_text
                        
    def remove_hints(self):
        """
        Removes hints by converting fields back to empty strings if their value matches the hint text in self.hints_dictionary.
        Dynamically parses hint keys (e.g., "['layout']['xaxis']['title']") to access and update fields in self.fig_dict.
        The hints_dictionary is first populated during creation of the class object in __init__.
        """
        for hint_key, hint_text in self.hints_dictionary.items():
            # Parse the hint_key into a list of keys representing the path in the record.
            # For example, if hint_key is "['layout']['xaxis']['title']",
            # then record_path_as_list will be ['layout', 'xaxis', 'title'].
            record_path_as_list = hint_key.strip("[]").replace("'", "").split("][")
            record_path_length = len(record_path_as_list)
            # Start at the top-level record dictionary.
            current_field = self.fig_dict

            # Loop over each key in the path.
            # For example, with record_path_as_list = ['layout', 'xaxis', 'title']:
            #    at nesting_level 0, current_path_key will be "layout";
            #    at nesting_level 1, current_path_key will be "xaxis";  <-- (this is the "xaxis" example)
            #    at nesting_level 2, current_path_key will be "title".  
            # Enumerate with a starting index of 1.
            for nesting_level, current_path_key in enumerate(record_path_as_list, start=1):
                # If not the final depth key, then retrieve from deeper.
                if nesting_level != record_path_length: 
                    current_field = current_field.get(current_path_key, {})  # `get` will return the second argument if the requested field does not exist.
                else:
                    # Final key: if the field's value equals the hint text, reset it to an empty string.
                    if current_field.get(current_path_key, "") == hint_text:
                        current_field[current_path_key] = ""

    #Make some pointers to external functions, for convenience, so people can use syntax like record.function_name() if desired.
    def apply_style(self, style_name):
        self.fig_dict = apply_style_to_plotly_dict(self.fig_dict, style_name=style_name)
    def validate_JSONGrapher_record(self):
        validate_JSONGrapher_record(self)
    def update_and_validate_JSONGrapher_record(self):
        update_and_validate_JSONGrapher_record(self)

# helper function to validate x axis and y axis labels.
# label string will be the full label including units. Axis_name is typically "x" or "y"
def validate_JSONGrapher_axis_label(label_string, axis_name="", remove_plural_units=True):
    """
    Validates the axis label provided to JSONGrapher.

    Args:
        label_string (str): The axis label containing a numeric value and units.
        axis_name (str): The name of the axis being validated (e.g., 'x' or 'y').
        remove_plural_units (boolean) : Instructions wil to remove plural units or not. Will remove them in the returned stringif set to True, or will simply provide a warning if set to False.

    Returns:
        None: Prints warnings if any validation issues are found.
    """
    warnings_list = []
    
    #First check if the label is empty.
    if label_string == '':
        warnings_list.append(f"Your {axis_name} axis label is an empty string. JSONGrapher records should not have empty strings for axis labels.")
    else:    
        parsing_result = separate_label_text_from_units(label_string)  # Parse the numeric value and units from the label string
        # Check if units are missing
        if parsing_result["units"] == "":
            warnings_list.append(f"Your {axis_name} axis label is missing units. JSONGrapher is expected to handle axis labels with units, with the units between parentheses '( )'.")    
        # Check if the units string has balanced parentheses
        open_parens = parsing_result["units"].count("(")
        close_parens = parsing_result["units"].count(")")
        if open_parens != close_parens:
            warnings_list.append(f"Your {axis_name} axis label has unbalanced parentheses in the units. The number of opening parentheses '(' must equal the number of closing parentheses ')'.")
    
    #now do the plural units check.
    units_changed_flag, units_singularized = units_plural_removal(parsing_result["units"])
    if units_changed_flag == True:
        warnings_list.append("The units of " + parsing_result["units"] + " appear to be plural. Units should be entered as singular, such as 'year' rather than 'years'.")
        if remove_plural_units==True:
            label_string = parsing_result["text"] + " (" + units_singularized + ")"
            warnings_list.append("Now removing the 's' to change the units into singular '" + units_singularized + "'.  To avoid this change, use the function you've called with the optional argument of remove_plural_units set to False.")
    else:
        pass

    # Return validation result
    if warnings_list:
        print(f"Warning: Your  {axis_name} axis label did not pass expected vaidation checks. You may use Record.set_x_axis_label() or Record.set_y_axis_label() to change the labels. The validity check fail messages are as follows: \n", warnings_list)
        return False, warnings_list, label_string
    else:
        return True, [], label_string    
    
def units_plural_removal(units_to_check):
    """
    Parses a units string to remove "s" if the string is found as an exact match without an s in the units lists.
    Args:
        units_to_check (str): A string containing units to check.

    Returns:
        tuple: A tuple of two values
              - "changed" (Boolean): True, or False, where True means the string was changed to remove an "s" at the end.
              - "singularized" (string): The units parsed to be singular, if needed.
    """
    #first check if we have the module we need. If not, return with no change.
    
    try:
        import JSONGrapherRC.units_list as units_list
    except:
        units_changed_flag = False
        return units_changed_flag, units_to_check #return None if there was no test.
    #First try to check if units are blank or ends with "s" is in the units list. 

    if (units_to_check == "") or (units_to_check[-1] != "s"):
        units_changed_flag = False
        units_singularized = units_to_check #return if string is blank or does not end with s.
    elif (units_to_check != "") and (units_to_check[-1] == "s"): #continue if not blank and ends with s. 
        if (units_to_check in units_list.expanded_ids_set) or (units_to_check in units_list.expanded_names_set):#return unchanged if unit is recognized.
            units_changed_flag = False
            units_singularized = units_to_check #No change if was found.
        else:
            truncated_string = units_to_check[0:-1] #remove last letter.
            if (truncated_string in units_list.expanded_ids_set) or (truncated_string in units_list.expanded_names_set):
                units_changed_flag = True
                units_singularized = truncated_string #return without the s.   
            else: #No change if the truncated string isn't found.
                units_changed_flag = False
                units_singularized = units_to_check
    return units_changed_flag, units_singularized


def separate_label_text_from_units(label_with_units):
    """
    Parses a label with text string and units in parentheses after that to return the two parts.

    Args:
        value (str): A string containing a label and optional units enclosed in parentheses.
                     Example: "Time (Years)" or "Speed (km/s)

    Returns:
        dict: A dictionary with two keys:
              - "text" (str): The label text parsed from the input string.
              - "units" (str): The units parsed from the input string, or an empty string if no units are present.
    """
    # Find the position of the first '(' and the last ')'
    start = label_with_units.find('(')
    end = label_with_units.rfind(')')
    
    # Ensure both are found and properly ordered
    if start != -1 and end != -1 and end > start:
        text_part = label_with_units[:start].strip()  # Everything before '('
        units_part = label_with_units[start + 1:end].strip()  # Everything inside '()'
    else:
        text_part = label_with_units
        units_part = ""
    parsed_output = {
                "text":text_part,
                "units":units_part
            }
    return parsed_output


def validate_plotly_data_list(data):
    """
    Validates the entries in a Plotly data array.
    If a dictionary is received, the function will assume you are sending in a single dataseries for validation
    and will put it in a list of one before the validation.

    Args:
        data (list): A list of dictionaries, each representing a Plotly trace.

    Returns:
        bool: True if all entries are valid, False otherwise.
        list: A list of errors describing why the validation failed.
    """
    #check if a dictionary was received. If so, will assume that
    #a single series has been sent, and will put it in a list by itself.
    if type(data) == type({}):
        data = [data]

    required_fields_by_type = {
        "scatter": ["x", "y"],
        "bar": ["x", "y"],
        "pie": ["labels", "values"],
        "heatmap": ["z"],
    }
    
    warnings_list = []

    for i, trace in enumerate(data):
        if not isinstance(trace, dict):
            warnings_list.append(f"Trace {i} is not a dictionary.")
            continue
        if "comments" in trace:
            warnings_list.append(f"Trace {i} has a comments field within the data. This is allowed by JSONGrapher, but is discouraged by plotly. By default, this will be removed when you export your record.")
        # Determine the type based on the fields provided
        trace_type = trace.get("type")
        if not trace_type:
            # Infer type based on fields and attributes
            if "x" in trace and "y" in trace:
                if "mode" in trace or "marker" in trace or "line" in trace:
                    trace_type = "scatter"
                elif "text" in trace or "marker.color" in trace:
                    trace_type = "bar"
                else:
                    trace_type = "scatter"  # Default assumption
            elif "labels" in trace and "values" in trace:
                trace_type = "pie"
            elif "z" in trace:
                trace_type = "heatmap"
            else:
                warnings_list.append(f"Trace {i} cannot be inferred as a valid type.")
                continue
        
        # Check for required fields
        required_fields = required_fields_by_type.get(trace_type, [])
        for field in required_fields:
            if field not in trace:
                warnings_list.append(f"Trace {i} (type inferred as {trace_type}) is missing required field: {field}.")

    if warnings_list:
        print("Warning: There are some entries in your data list that did not pass validation checks: \n", warnings_list)
        return False, warnings_list
    else:
        return True, []

def parse_units(value):
    """
    Parses a numerical value and its associated units from a string. This meant for scientific constants and parameters
    Such as rate constants, gravitational constant, or simiilar.

    Args:
        value (str): A string containing a numeric value and optional units enclosed in parentheses.
                     Example: "42 (kg)" or "100".

    Returns:
        dict: A dictionary with two keys:
              - "value" (float): The numeric value parsed from the input string.
              - "units" (str): The units parsed from the input string, or an empty string if no units are present.
    """
    # Find the position of the first '(' and the last ')'
    start = value.find('(')
    end = value.rfind(')')
    
    # Ensure both are found and properly ordered
    if start != -1 and end != -1 and end > start:
        number_part = value[:start].strip()  # Everything before '('
        units_part = value[start + 1:end].strip()  # Everything inside '()'
        parsed_output = {
            "value": float(number_part),  # Convert number part to float
            "units": units_part  # Extracted units
        }
    else:
        parsed_output = {
            "value": float(value),  # No parentheses, assume the entire string is numeric
            "units": ""  # Empty string represents absence of units
        }
    
    return parsed_output


#This function sets the plot_type of a data_series_dict
#based on some JSONGrapherRC options.
#It calls "plot_type_to_field_values" 
#and then updates the data_series accordingly, as needed.
def set_data_series_dict_plot_type(data_series_dict, plot_type=""):
    if plot_type == "":
        plot_type = data_series_dict.get('type', 'scatter') #get will return the second argument if the first argument is not present.       
    #We need to be careful about one case: in plotly, a "spline" is declared a scatter plot with data.line.shape = spline. 
    #So we need to check if we have spline set, in which case we make the plot_type scatter_spline when calling plot_type_to_field_values.
    shape_field = data_series_dict.get('line', {}).get('shape', '') #get will return first argument if there, second if not, so can chain things.
    if shape_field == 'spline':
        plot_type = 'scatter_spline'
    fields_dict = plot_type_to_field_values(plot_type)
 
    
    #update the data_series_dict.
    if fields_dict.get("mode_field"):
        data_series_dict["mode"] = fields_dict["mode_field"]
    if fields_dict.get("type_field"):
        data_series_dict["type"] = fields_dict["type_field"]
    if fields_dict.get("line_shape_field") != "":
        data_series_dict.setdefault("line", {"shape": ''})  # Creates the field if it does not already exist.
        data_series_dict["line"]["shape"] = fields_dict["line_shape_field"]
    return data_series_dict

def plot_type_to_field_values(plot_type):
    """
    Takes in a string that is a plot type, such as "scatter", "scatter_spline", etc.
    and returns the field values that would have to go into a plotly data object.

    Returns:
        dict: A dictionary with keys and values for the fields that will be ultimately filled.

    To these fields are used in the function set_plot_type_one_data_series

    """
    fields_dict = {}
    #initialize some variables.
    fields_dict["type_field"] = plot_type.lower()
    fields_dict["mode_field"] = None
    fields_dict["line_shape_field"] = None
    # Assign the various types. This list of values was determined 'manually'.
    if plot_type.lower() == "scatter":
        fields_dict["type_field"] = "scatter"
        fields_dict["mode_field"] = "markers"
        fields_dict["line_shape_field"] = None
    elif plot_type.lower() == "scatter_spline":
        fields_dict["type_field"] = "scatter"
        fields_dict["mode_field"] = None
        fields_dict["line_shape_field"] = "spline"
    elif plot_type.lower() == "spline":
        fields_dict["type_field"] = 'scatter'
        fields_dict["mode_field"] = 'lines'
        fields_dict["line_shape_field"] = "spline"
    return fields_dict

#This function does updating of internal things before validating
#This is used before printing and returning the JSON record.
def update_and_validate_JSONGrapher_record(record):
    record.update_plot_types()
    record.validate_JSONGrapher_record()
    record.fig_dict = clean_json_fig_dict(record.fig_dict)
    return record

#TODO: add the ability for this function to check against the schema.
def validate_JSONGrapher_record(record):
    """
    Validates a JSONGrapher record to ensure all required fields are present and correctly structured.

    Args:
        record (dict): The JSONGrapher record to validate.

    Returns:
        bool: True if the record is valid, False otherwise.
        list: A list of errors describing any validation issues.
    """
    warnings_list = []

    # Check top-level fields
    if not isinstance(record, dict):
        return False, ["The record is not a dictionary."]
    
    # Validate "comments"
    if "comments" not in record:
        warnings_list.append("Missing top-level 'comments' field.")
    elif not isinstance(record["comments"], str):
        warnings_list.append("'comments' is a recommended field and should be a string with a description and/or metadata of the record, and citation references may also be included.")
    
    # Validate "datatype"
    if "datatype" not in record:
        warnings_list.append("Missing 'datatype' field.")
    elif not isinstance(record["datatype"], str):
        warnings_list.append("'datatype' should be a string.")
    
    # Validate "data"
    if "data" not in record:
        warnings_list.append("Missing top-level 'data' field.")
    elif not isinstance(record["data"], list):
        warnings_list.append("'data' should be a list.")
        validate_plotly_data_list(record["data"]) #No need to append warnings, they will print within that function.
    
    # Validate "layout"
    if "layout" not in record:
        warnings_list.append("Missing top-level 'layout' field.")
    elif not isinstance(record["layout"], dict):
        warnings_list.append("'layout' should be a dictionary.")
    else:
        # Validate "layout" subfields
        layout = record["layout"]
        
        # Validate "title"
        if "title" not in layout:
            warnings_list.append("Missing 'layout.title' field.")
        # Validate "title.text"
        elif "text" not in layout["title"]:
            warnings_list.append("Missing 'layout.title.text' field.")
        elif not isinstance(layout["title"]["text"], str):
            warnings_list.append("'layout.title.text' should be a string.")
        
        # Validate "xaxis"
        if "xaxis" not in layout:
            warnings_list.append("Missing 'layout.xaxis' field.")
        elif not isinstance(layout["xaxis"], dict):
            warnings_list.append("'layout.xaxis' should be a dictionary.")
        else:
            # Validate "xaxis.title"
            if "title" not in layout["xaxis"]:
                warnings_list.append("Missing 'layout.xaxis.title' field.")
            elif "text" not in layout["xaxis"]["title"]:
                warnings_list.append("Missing 'layout.xaxis.title.text' field.")
            elif not isinstance(layout["xaxis"]["title"]["text"], str):
                warnings_list.append("'layout.xaxis.title.text' should be a string.")
        
        # Validate "yaxis"
        if "yaxis" not in layout:
            warnings_list.append("Missing 'layout.yaxis' field.")
        elif not isinstance(layout["yaxis"], dict):
            warnings_list.append("'layout.yaxis' should be a dictionary.")
        else:
            # Validate "yaxis.title"
            if "title" not in layout["yaxis"]:
                warnings_list.append("Missing 'layout.yaxis.title' field.")
            elif "text" not in layout["yaxis"]["title"]:
                warnings_list.append("Missing 'layout.yaxis.title.text' field.")
            elif not isinstance(layout["yaxis"]["title"]["text"], str):
                warnings_list.append("'layout.yaxis.title.text' should be a string.")
    
    # Return validation result
    if warnings_list:
        print("Warning: There are missing fields in your JSONGrapher record: \n", warnings_list)
        return False, warnings_list
    else:
        return True, []

def rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2):
    """
    Applies a rolling polynomial regression with a specified window size and degree.

    Args:
        x_values (list): List of x coordinates.
        y_values (list): List of y coordinates.
        window_size (int): Number of points per rolling fit (default: 3).
        degree (int): Degree of polynomial to fit (default: 2).

    Returns:
        tuple: (smoothed_x, smoothed_y) lists for plotting.
    """
    import numpy as np
    smoothed_y = []
    smoothed_x = x_values  # Keep x values unchanged

    half_window = window_size // 2  # Number of points to take before & after

    for i in range(len(y_values)):
        # Handle edge cases: First and last points have fewer neighbors
        left_bound = max(0, i - half_window)
        right_bound = min(len(y_values), i + half_window + 1)

        # Select the windowed data
        x_window = np.array(x_values[left_bound:right_bound])
        y_window = np.array(y_values[left_bound:right_bound])

        # Fit polynomial & evaluate at current point
        poly_coeffs = np.polyfit(x_window, y_window, deg=degree)
        smoothed_y.append(np.polyval(poly_coeffs, x_values[i]))

    return smoothed_x, smoothed_y


def convert_JSONGrapher_dict_to_matplotlib_fig(fig_dict):
    """
    Converts a Plotly figure dictionary into a Matplotlib figure without using pio.from_json.

    Args:
        fig_dict (dict): A dictionary representing a Plotly figure.

    Returns:
        matplotlib.figure.Figure: The corresponding Matplotlib figure.
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    # Extract traces (data series)
    for trace in fig_dict.get("data", []):
        trace_type = trace.get("type", None)
        # If type is missing, but mode indicates lines and shape is spline, assume it's a spline
        if not trace_type and trace.get("mode") == "lines" and trace.get("line", {}).get("shape") == "spline":
            trace_type = "spline"

        x_values = trace.get("x", [])
        y_values = trace.get("y", [])
        trace_name = trace.get("name", "Data")
        if trace_type == "bar":
            ax.bar(x_values, y_values, label=trace_name)

        elif trace_type == "scatter":
            mode = trace.get("mode", "")
            ax.scatter(x_values, y_values, label=trace_name, alpha=0.7)

            # Attempt to simulate spline behavior if requested
            if "lines" in mode or trace.get("line", {}).get("shape") == "spline":
                print("Warning: Rolling polynomial approximation used instead of spline.")
                x_smooth, y_smooth = rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2)
                
                # Add a label explicitly for the legend
                ax.plot(x_smooth, y_smooth, linestyle="-", label=f"{trace_name} Spline")
        elif trace_type == "spline":
            print("Warning: Using rolling polynomial approximation instead of true spline.")
            x_smooth, y_smooth = rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2)
            ax.plot(x_smooth, y_smooth, linestyle="-", label=f"{trace_name} Spline")

    # Extract layout details
    layout = fig_dict.get("layout", {})
    title = layout.get("title", {})
    if isinstance(title, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        ax.set_title(title.get("text", "Converted Plotly Figure"))
    else:
        ax.set_title(title if isinstance(title, str) else "Converted Plotly Figure")

    xaxis = layout.get("xaxis", {})
    xlabel = "X-Axis"  # Default label
    if isinstance(xaxis, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        title_obj = xaxis.get("title", {})
        xlabel = title_obj.get("text", "X-Axis") if isinstance(title_obj, dict) else title_obj
    elif isinstance(xaxis, str):
        xlabel = xaxis  # If it's a string, use it directly
    ax.set_xlabel(xlabel)
    yaxis = layout.get("yaxis", {})
    ylabel = "Y-Axis"  # Default label
    if isinstance(yaxis, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        title_obj = yaxis.get("title", {})
        ylabel = title_obj.get("text", "Y-Axis") if isinstance(title_obj, dict) else title_obj
    elif isinstance(yaxis, str):
        ylabel = yaxis  # If it's a string, use it directly
    ax.set_ylabel(ylabel)
    ax.legend()
    return fig
    




#The below function works, but because it depends on the python plotly package, we avoid using it
#To decrease the number of dependencies. 
def convert_plotly_dict_to_matplotlib(fig_dict):
    """
    Converts a Plotly figure dictionary into a Matplotlib figure.

    Supports: Bar Charts, Scatter Plots, Spline curves using rolling polynomial regression.

    This functiony has a dependency on the plotly python package (pip install plotly)

    Args:
        fig_dict (dict): A dictionary representing a Plotly figure.

    Returns:
        matplotlib.figure.Figure: The corresponding Matplotlib figure.
    """
    import plotly.io as pio

    # Convert JSON dictionary into a Plotly figure
    plotly_fig = pio.from_json(json.dumps(fig_dict))

    # Create a Matplotlib figure
    fig, ax = plt.subplots()

    for trace in plotly_fig.data:
        if trace.type == "bar":
            ax.bar(trace.x, trace.y, label=trace.name if trace.name else "Bar Data")

        elif trace.type == "scatter":
            mode = trace.mode if isinstance(trace.mode, str) else ""
            line_shape = trace.line["shape"] if hasattr(trace, "line") and "shape" in trace.line else None

            # Plot raw scatter points
            ax.scatter(trace.x, trace.y, label=trace.name if trace.name else "Scatter Data", alpha=0.7)

            # If spline is requested, apply rolling polynomial smoothing
            if line_shape == "spline" or "lines" in mode:
                print("Warning: During the matploglib conversion, a rolling polynomial will be used instead of a spline, whereas JSONGrapher uses a true spline.")
                x_smooth, y_smooth = rolling_polynomial_fit(trace.x, trace.y, window_size=3, degree=2)
                ax.plot(x_smooth, y_smooth, linestyle="-", label=trace.name + " Spline" if trace.name else "Spline Curve")

    ax.legend()
    ax.set_title(plotly_fig.layout.title.text if plotly_fig.layout.title else "Converted Plotly Figure")
    ax.set_xlabel(plotly_fig.layout.xaxis.title.text if plotly_fig.layout.xaxis.title else "X-Axis")
    ax.set_ylabel(plotly_fig.layout.yaxis.title.text if plotly_fig.layout.yaxis.title else "Y-Axis")

    return fig
    

def apply_style_to_plotly_dict(plotly_json, style_name):
    """
    Apply a predefined style to a Plotly JSON object based on a style name which may be a journal name.
    
    :param plotly_json: dict, Plotly JSON object.
    :param style_name: str, Name of the style or journal.
    :return: dict, Updated Plotly JSON object.
    """
    styles_available = {
        "Nature": {
            "layout": {
                "title": {"font": {"size": 24, "family": "Times New Roman", "color": "black"}},
                "font": {"size": 18, "family": "Times New Roman"},
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
            }
        },
        "Science": {
            "layout": {
                "title": {"font": {"size": 22, "family": "Arial", "color": "black"}},
                "font": {"size": 16, "family": "Arial"},
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
            }
        }
    }

    # Get the style for the specified journal, default to no change if not found
    style_dict = styles_available.get(style_name, {})
    
    # Ensure title field is merged properly to avoid overwriting
    plotly_json.setdefault("layout", {})
    plotly_json["layout"].setdefault("title", {})
    
    # Merge title settings separately to preserve existing text
    plotly_json["layout"]["title"] = {**plotly_json["layout"]["title"], **style_dict.get("layout", {}).get("title", {})}
    
    # Merge other layout settings
    for key, value in style_dict.get("layout", {}).items():
        if key != "title":  # Skip title since it was handled separately
            plotly_json["layout"][key] = value
    
    return plotly_json


def update_title_field(data, depth=1, max_depth=10):
    """ This function is intended to make JSONGrapher .json files compatible with the newer plotly recommended title field formatting
    which is necessary to do things like change the font, and also necessary for being able to convert a JSONGrapher json_dict to python plotly figure objects. """
    """ Recursively checks for 'title' fields and converts them to dictionary format. """
    if depth > max_depth or not isinstance(data, dict):
        return data
    
    for key, value in data.items():
        if key == "title" and isinstance(value, str):
            data[key] = {"text": value}
        elif isinstance(value, dict):  # Nested dictionary
            data[key] = update_title_field(value, depth + 1, max_depth)
        elif isinstance(value, list):  # Lists can contain nested dictionaries
            data[key] = [update_title_field(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in value]
    
    return data

def remove_extra_information_field(data, depth=1, max_depth=10):
    """ This function is intended to make JSONGrapher .json files compatible with the current plotly format expectations
     and also necessary for being able to convert a JSONGRapher json_dict to python plotly figure objects. """
    """Recursively checks for 'extraInformation' fields and removes them."""
    if depth > max_depth or not isinstance(data, dict):
        return data

    # Use a copy of the dictionary keys to safely modify the dictionary during iteration
    for key in list(data.keys()):
        if key == "extraInformation":
            del data[key]  # Remove the field
        elif isinstance(data[key], dict):  # Nested dictionary
            data[key] = remove_extra_information_field(data[key], depth + 1, max_depth)
        elif isinstance(data[key], list):  # Lists can contain nested dictionaries
            data[key] = [
                remove_extra_information_field(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in data[key]
            ]
    
    return data
    

def remove_nested_comments(data, top_level=True):
    """ This function is intended to make JSONGrapher .json files compatible with the current plotly format expectations
     and also necessary for being able to convert a JSONGRapher json_dict to python plotly figure objects. """
    """Removes 'comments' fields that are not at the top level of the JSON-dict. Starts with 'top_level = True' when dict is first passed in then becomes false after that. """
    if not isinstance(data, dict):
        return data

    # Process nested structures
    for key in list(data.keys()):
        if isinstance(data[key], dict):  # Nested dictionary
            data[key] = remove_nested_comments(data[key], top_level=False)
        elif isinstance(data[key], list):  # Lists can contain nested dictionaries
            data[key] = [
                remove_nested_comments(item, top_level=False) if isinstance(item, dict) else item for item in data[key]
            ]

    # Only remove 'comments' if not at the top level
    if not top_level:
        data = {k: v for k, v in data.items() if k != "comments"}

    return data

def clean_json_fig_dict(json_fig_dict, fields_to_update=["title_field", "extraInformation", "nested_comments"]):
    """ This function is intended to make JSONGrapher .json files compatible with the current plotly format expectations
     and also necessary for being able to convert a JSONGRapher json_dict to python plotly figure objects. """
    data = json_fig_dict
    #unmodified_data = copy.deepcopy(data)
    if "title_field" in fields_to_update:
        data = update_title_field(data)
    if "extraInformation" in fields_to_update:
        data = remove_extra_information_field(data)
    if "nested_comments" in fields_to_update:
        data = remove_nested_comments(data)
    return data
    

# Example Usage
if __name__ == "__main__":
    # Example of creating a record with optional attributes.
    record = JSONGrapherRecord(
        comments="Here is a description.",
        graph_title="Here Is The Graph Title Spot",
        data_objects_list=[
            {"comments": "Initial data series.", "uid": "123", "name": "Series A", "type": "spline", "x": [1, 2, 3], "y": [4, 5, 8]}
        ],
    )
    record.export_to_json_file("test.json")
    print(record)

    # Example of creating a record from an existing dictionary.
    existing_JSONGrapher_record = {
        "comments": "Existing record description.",
        "graph_title": "Existing Graph",
        "data": [
            {"comments": "Data series 1", "uid": "123", "name": "Series A", "type": "spline", "x": [1, 2, 3], "y": [4, 5, 8]}
        ],
    }
    record_from_existing = JSONGrapherRecord(existing_JSONGrapher_record=existing_JSONGrapher_record)
    print(record)
    
    