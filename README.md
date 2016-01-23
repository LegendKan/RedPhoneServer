# RedPhoneServer
The server work only with REST protocol
The ZRTP part is not included.
This server developed for couple days for fun and posted as is
without any optimizations for production version.
It developed without any documentations. I just parsed Signal-Android
code and write a server for it. Maybe some method not correct, but it work)
Use it only for education!

And if you want to use secure calls you need to write your own TURN server
for zrtp connections between phones. Without it you will get only requests
from one phone to another.

"redphonectl" starts django over tornado which shoul work with a signal's
database and answer to registration requests.

master.py starts non-blocking sockets for master-redphone connections
which handles phone connections for rings. By the plan it should work
with the django(with wsgi and app), but something went wrong...Haven't
have enough time for modifications.

How to start:

python tornado_red.py 8080

python master.py
