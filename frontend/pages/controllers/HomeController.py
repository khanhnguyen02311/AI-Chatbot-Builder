from datetime import datetime

def validate_login_input(data):
	if data is None:
		if data["password"] != data["password_re"]:
			return False, "Password does not match"