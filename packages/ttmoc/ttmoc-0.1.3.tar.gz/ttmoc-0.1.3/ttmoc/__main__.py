"""
Entry point for running ttmoc as a module.
Example: python -m ttmoc --api-url http://localhost:8000 --tenant-id your-tenant-id
"""
from .cli import main

if __name__ == "__main__":
    main()
