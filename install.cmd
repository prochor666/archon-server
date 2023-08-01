@ECHO OFF
cls
WHERE /Q python3

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

WHERE /Q pip3

IF %ERRORLEVEL% NEQ 0 (
    ECHO PIP 3 is required
    EXIT /B 0
) ELSE (
    pip3 install pymongo
    pip3 install pyyaml
    pip3 install pyopenssl
    pip3 install pyIsEmail
    pip3 install psutil
    pip3 install websocket
    pip3 install websocket-client
    pip3 install dnspython
    pip3 install python-slugify
    pip3 install asyncssh
    pip3 install nest_asyncio
    pip3 install requests
    pip3 install uvicorn
    pip3 install fastapi
    pip3 install mysql-connector-python
    pip3 install colorama
    pip3 install jinja2
    pip3 install pytz

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
