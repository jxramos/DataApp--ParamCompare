window.onload = function () {
    console.log("window onload")

    // submit button will be disabled until all required inputs are satisfied
    submit_button = document.getElementById('submit');
    submit_button.disabled = true;

    // setup the change event callbacks
    document.getElementById('file_x').addEventListener('change', data_change_event, false );
    document.getElementById('file_y').addEventListener('change', data_change_event, false );
}

function data_change_event() {
    // trigger the enabling of the submit button
    enable_submit()

    // ascertain parameter set overlap for analysis
    update_parameters()
}


function enable_submit() {
    // Enables the submit button should all required inputs be present
    console.log("enable_submit")
    is_enabled = document.getElementById('file_x').value &&
                 document.getElementById('file_y').value;
    document.getElementById('submit').disabled = ! is_enabled
}

function _update_parameters() {
    text_x = file_reader_x.result;
    text_y = file_reader_y.result;

    if ( ! text_x || ! text_y ){
        return;
    }

    // Retrieve CSV header columns
    x_lines = text_x.split("\n");
    y_lines = text_y.split("\n");

    x_cols = x_lines[0].split(",");
    y_cols = y_lines[0].split(",");

    // Update the parameter candidates to only those common columns
    id_col = document.getElementById('id_col').value
    common_cols = x_cols.filter( element => y_cols.indexOf(element) !== -1 && element != id_col );
    params.options.length = 0 
    for ( i=0; i < common_cols.length ; i++ ){
        col = common_cols[i]
        params.options[i] = new Option(col,col)
    }
    console.log("updating parameters to : " + common_cols )
}

function update_parameters() {
    // Guard Clause: ensure that both input files exist
    if ( document.getElementById('submit').disabled ) {
        return;
    }

    // Read the header rows for each file
    blob_x = document.getElementById('file_x').files[0];
    blob_y = document.getElementById('file_y').files[0];

    file_reader_x = new FileReader();
    file_reader_y = new FileReader();

    file_reader_x.onload = function(e) {
        _update_parameters();
      }
      file_reader_y.onload = function(e) {
        _update_parameters();
      }

    file_reader_x.readAsText( blob_x , 'utf-8');
    file_reader_y.readAsText( blob_y , 'utf-8');
}