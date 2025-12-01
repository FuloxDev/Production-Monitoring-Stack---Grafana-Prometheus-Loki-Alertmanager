import getpass
import bcrypt
import yaml
import os

# Get username and password from user
username = input("Username: ")
password = getpass.getpass("Password: ")

# Hash the password
hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

# Prepare the data to be saved in YAML format with SSL config
data = {
    'tls_server_config': {
        'cert_file': '/certs/prometheus.crt',
        'key_file': '/certs/prometheus.key',
        'min_version': 'TLS12',
        'max_version': 'TLS13',
        'cipher_suites': [
            'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
            'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384'
        ],
        'prefer_server_cipher_suites': True
    },
    'basic_auth_users': {
        username: hashed_password.decode()
    }
}


# Save the data to web.yml file in config directory
with open('web.yml', 'w') as file:
    yaml.dump(data, file, default_flow_style=False)

print("Credentials and SSL configuration saved successfully")
print(f"Username: {username}")
print(f"Hashed password: {hashed_password.decode()}")
print(f"File created at: config/web.yml")