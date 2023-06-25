from fastapi import FastAPI


def read():

    description = """
    Archon server helps you do awesome stuff. 🚀

    ## Items

    You can **read items**.

    ## Users

    You will be able to:

    * **Create users** (_not implemented_).
    * **Read users** (_not implemented_).
    """

    default  = {
        "title": "Archon server",
        "description": description,
        "version": "0.1.0",
        "terms_of_service": "https://github.com/prochor666/archon-server",
        "contact": {
            "name": "Prochor666",
            "url": "https://github.com/prochor666/archon-server",
            "email": "prochor666@gmail.com",
        },
        "license_info": {
            "name": "MIT",
            "url": "https://choosealicense.com/licenses/mit/",
        },
        "openapi_tags": [
            {
                "name": "Common",
                "description": "Common API utilities",
            },
            {
                "name": "System",
                "description": "System (HW/OS) API utilities",
            },
        ]
    }


    return default