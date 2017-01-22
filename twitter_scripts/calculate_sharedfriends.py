import database
import sys

db = database.Database(sys.argv[1])
db.calculate_sharedfriends()