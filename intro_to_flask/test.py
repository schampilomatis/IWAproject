from RDFhandler import authenticate,checkEmail
from werkzeug import generate_password_hash, check_password_hash
print generate_password_hash('123')
#print authenticate("schampilomatis@gmail.com","123")