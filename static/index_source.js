window.onload = function () {
    console.log("window onload")

    // submit button will be disabled until all required inputs are satisfied
    submit_button = document.getElementById('submit');
    submit_button.disabled = true;

    // setup the change event callbacks to trigger the enabling of the submit button
    document.getElementById('file_x').addEventListener('change', enable_submit, false );
    document.getElementById('file_y').addEventListener('change', enable_submit, false );
}

function enable_submit() {
    // Enables the submit button should all required inputs be present
    console.log("enable_submit")
    is_enabled = document.getElementById('file_x').value &&
                 document.getElementById('file_y').value;
    document.getElementById('submit').disabled = ! is_enabled
}