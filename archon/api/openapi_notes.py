from fastapi import FastAPI


def read():

    description = """
    Archon server helps you do awesome stuff. 🚀

    ## Items

    You can **read items**.

    ## Users

    You can create and activate user
    """

    default  = {
        "title": "Archon server",
        "description": description,
        "version": "0.2.0",
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