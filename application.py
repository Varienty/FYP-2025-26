"""
Application entry point for AWS Elastic Beanstalk.
Re-exports the WSGI application from wsgi module.
"""
from wsgi import application

__all__ = ['application']
