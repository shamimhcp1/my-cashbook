
// JavaScript/jQuery code for delete-button
$(document).ready(function() {

  // Click event handler for the Delete button
  $("#delete-button").click(function(e) {
    e.preventDefault(); // Prevent the default form submission

    if (window.confirm("Are you sure you want to delete this?")) {
      $("#delete-form").submit();  // Submit the Delete form
    }
  });
});
