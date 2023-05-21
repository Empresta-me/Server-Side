# Server-Side
API and Message Broker and Peer-to-Peer. 

## How to run
```
python Community.py --pem testpassword
```

## How to register an account

- Authenticate yourself to the server to get an association token (/auth/associate)
- Combine the association token with a public key to get a challenge (/auth/challenge)
- Register an account or login with the issue challenged + a signature (/auth/register)
