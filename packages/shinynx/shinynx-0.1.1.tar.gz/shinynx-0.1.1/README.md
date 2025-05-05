# sticky nginx sessions and shiny

If you want to self-host your py-shiny app and your frontend is nginx this repo
shows how to configure multiple shiny instances for the backend (to handle e.g. load).

This package hooks the import of the shiny app to augment it with a cookie that nginx can use
to target a unique backend.

Shiny uses websockets so of course if you are behind - say - a CloudFlare firewall then this might not work
at *all* unless websocket traffic has been enabled.


## An example

The shiny `testapp` is based on the [load balancer example](https://github.com/posit-dev/py-shiny/blob/7ba8f90a44ee25f41aa8c258eceeba6807e0017a/examples/load_balance/app.py) from the py-shiny github and can
test the correctness of the setup.

Run a foreground nginx process on port 8080 with

```bash
nginx -c $(realpath .)/templates/sticky.conf
```
It assumes there are 4 unix domain socket endpoints `app{n}.sock` in this directory.

Now run multiple background shiny instances:

```bash
# start 4 uvicorn processes holding one testapp shiny instance each
python -m shinynx.run --workers=4 testapp.core
# OR try the express version
python -m shinynx.run --workers=4 --express testapp.express
```

This serves as a substitute for `shiny run testapp.core`

You will now see `app{n}.sock` files appear in this directory. These are the endpoints for each
of 4 shiny instances. (See the `--uds` option for `uvicorn`)


You can fire up multiple browser tabs to hit this website concurrently with:

```bash
# fire up 10 browser tabs looking at http://127.0.0.1:8080
python -m testapp.browser -n10
```

Note, we use unix domain sockets because they are safer (no direct internet access) and it is also
easier to isolate the endpoints to the directory where the code resides.

## Rationale

Shiny requires a "stickyness" i.e. it must always communicate with the *same* background
shiny instance. So the cookie setup in `shinynx/sticky.py` is the crucial enhancment required along with
the `hash $cookie_sticky consistent;` nginx configuration option.

The nginx load balancer should ensure that the processes are "sticky" using a
random "sticky" cookie. There are possibly better solutions if you have the "plus" version of nginx. But
this works with the open source version.

See [the shiny docs](https://shiny.posit.co/py/docs/deploy-on-prem.html#other-hosting-options).


Currently we set our cookie *value* to the uvicorn endpoint value (e.g. `app1.sock` or `app2.sock` etc.).
**But** there is no guarantee that nginx will initially map a cookie value of `app1.sock` to the
`app1.sock` process (it's a hash after all!).
