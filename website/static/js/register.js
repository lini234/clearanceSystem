// JavaScript for dynamically updating department options based on college selection
$(document).ready(function() {
  $('#college').change(function() {
    var college = $(this).val();
    $('#department').empty(); // Clear existing options
    if (college === 'CONAS') {
      $('#department').append('<option value="Computer Science">Computer Science</option>');
      $('#department').append('<option value="Biological Sciences">Biological Sciences</option>');
    } else if (college === 'CBSS') {
      $('#department').append('<option value="Accounting">Accounting</option>');
      $('#department').append('<option value="Economics">Economics</option>');
    }
  });
});