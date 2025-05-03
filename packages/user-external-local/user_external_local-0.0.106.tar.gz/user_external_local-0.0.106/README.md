# External User Local Python Package

The External User Local Python Package is a library designed to manage access tokens for external users. It provides
functions to insert, update, retrieve, and delete access tokens from a database. This library is intended to be used in
conjunction with your own project.

## Installation

-pip install user-external-local 0.0.25
-add to requirements.txt user-external-local== 0.0.25

# Importing the Library

from library import library_DB import Accsess_Token_Library

# Usage Example: assuming system_id=1

# Initialize the access token library

all methods are static, no initialize required

# Insert a new access token

UserExternal.insert_or_update_external_user_access_token("example_user", 123,1, "example_token","example_expiry","
example refresh")
notice! refresh and expiry arent a mandatory

# Update an existing access token

UserExternal.update_user_external(123, "updated_token")

# Retrieve an access token by profile ID

access_token = UserExternal.get_access_token_by_profile_id(123)

# Retrieve an access token by user name

access_token = UserExternal.get_access_token_by_user_name("example_user",1)

# Delete an access token by profile ID

UserExternal.delete_access_token_by_profile_id(123)

# Update an existing access token by username

UserExternal.update_user_external_by_user_name("example_user",1, "new_token")

