./templates/questionnaire.html
simple form submit name and atmost 5 selection of checkboxes to api written in backend.py
./backend.py
index():
return the questionnaire page to the client when the server is call in default

save_preferences():
when the server is called by POST with /preferences, this function help to load data from the form submit to database

result():
when the server is called by /result, get data from database and return with the templete result.html and present result

./templates result.html
present data that stored in database, but d3 visualize is not complete

the project is hosted on aws now
