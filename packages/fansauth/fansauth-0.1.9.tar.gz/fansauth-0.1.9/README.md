# Overview

Authorization server & library to ease setting up a site (so it can delegate authorization stuff out).

Includes:
- A docker image to run an authorization server (with UI)
- A Python library to be used in your site

# Code structure

    frontend/  # frontend of auth.fans656.me
    fansauth/
      server/  # auth server
      lib/     # `fansauth` python library for resource server

# Development

    build-frontend.sh

# Resource server usage

    from fastapi import FastAPI
    from fansauth import auth  # <--- import `auth`
    
    app = FastAPI()
    app = auth(app)  # <--- add authorization to app
    
    @app.get('/foo')
    def foo():
        return 'hello foo'

See `fansauth/lib/auth.py` for more detailed usage.
