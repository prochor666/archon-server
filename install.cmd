@ECHO OFF
cls
WHERE /Q python

ECHO archon installer

IF %ERRORLEVEL% NEQ 0 (
    ECHO Python 3 is required
    EXIT /B 0
)

FOR /F "tokens=2" %%G IN ('python -V') do (SET version_raw=%%G)

SET modified=%version_raw:.=%
SET /A num=%modified%+0

IF %num% LSS 3100 (
    ECHO Python 3.10.0 or newer is required
    EXIT /B 0
) ELSE (
    ECHO Python %version_raw% found
)

WHERE /Q pip

IF %ERRORLEVEL% NEQ 0 (
    ECHO PIP is required
    EXIT /B 0
) ELSE (
    pip install pymongo
    pip install pyyaml
    pip install pyopenssl
    pip install pyIsEmail
    pip install psutil
    pip install websocket
    pip install websocket-client
    pip install dnspython
    pip install python-slugify
    pip install asyncssh
    pip install requests
    pip install hypercorn
    pip install fastapi
    pip install mysql-connector-python
    pip install colorama
    pip install jinja2

    IF exist storage\sites (
        echo storage\sites exists
    ) ELSE (
        mkdir storage\sites && echo storage\sites created
    )

    IF exist storage\devices (
        echo storage\devices exists
    ) ELSE (
        mkdir storage\devices && echo storage\devices created
    )

    IF exist storage\resources (
        echo storage\resources exists
    ) ELSE (
        mkdir storage\resources && echo storage\resources created
    )

    IF exist storage\logs (
        echo storage\logs exists
    ) ELSE (
        mkdir storage\logs && echo storage\logs created
    )

    IF exist config\app.yaml (
        echo config\app.yaml exists
    ) ELSE (
        copy config\sample.app.yaml config\app.yaml && echo config\app.yaml created
    )

    IF exist config\api.yaml (
        echo config\api.yaml exists
    ) ELSE (
        copy config\sample.api.yaml config\api.yaml && echo config\api.yaml created
    )

    IF exist config\smtp.yaml (
        echo config\smtp.yaml exists
    ) ELSE (
        copy config\sample.smtp.yaml config\smtp.yaml && echo config\smtp.yaml created
    )
)
