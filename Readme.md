#  Books 
A simple project to look up isbns on amazon, and add them to a goodreads shelf.  requires a credential file with the requisite keys for both Amazon and Goodreads APIs.  Depends on a csv of book titles and authors, which is not posted.  

I've also messed around with a grammar for creating ideal book descriptions, based on my tastes.  Some of my favorites of are posed below.  Currently only 2 or 3 tuples.  

The goodreads part borrows heavily from sefakilic's more featured implementation, availible below.  I made a few minor changes to get reviews to work properly (for my purposes):  https://github.com/sefakilic/goodreads

The Amazon part makes use of yoavaviram's  library:  https://github.com/yoavaviram/python-amazon-simple-product-api

To do:
- Fix some issues with exclusively electronic books
- update so the whole thing, database included, is in python/pandas.  

Example Tuples:
"the truth about how a greek city did a nuclear strike on high school mathematics"
- The author of 300 gives his take on Pythagoras's Biography

"there is one more than forty nine stories of which mr cadwallader shampoos the individuals carrying out his vision."
- 50 shades of shampoo

"Alvin E. Roth is one of the americas experts of high level intrigue and has been on some of the losing sides of romes glorious conquests"
- Proffesor Roth's time-traveling career
