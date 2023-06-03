import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pyisemail import is_email
import pyisemail.diagnosis.valid_diagnosis, pyisemail.diagnosis.gtld_diagnosis
from archon import app, utils

# TO-DO: attachments as dict
# TO-DO: templates via built-in Jinja 2


def send(to: str, subject: str, body: str, att: str = '') -> bool | str:
    conf = app.config['smtp']
    if type(conf) is dict:
        return via(conf, email_compose({
            'from': conf['from'],
            'to': to,
            'subject': subject,
            'alt_body': utils.br2nl(utils.strip_tags(subject, '<br>')),
            'body': body
        }, att))

    return False


def via(conf: dict, msg: MIMEMultipart) -> bool | str:

    if conf['cs'] in ['TLS', 'SSL']:
        context = ssl.create_default_context()

        if conf['cs'] == 'SSL':
            try:
                with smtplib.SMTP_SSL(conf['host'], conf['port'], context=context) as server:
                    server.login(conf['username'], conf['password'])
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    return True

            except Exception as e:
                return 'SSL-error: ' + str(e)

        if conf['cs'] == 'TLS':
            # Try to log in to server and send email
            try:
                server = smtplib.SMTP(conf['host'], conf['port'])
                server.ehlo()
                server.starttls(context=context)  # Secure the connection
                server.ehlo()
                server.login(conf['username'], conf['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                return True

            except Exception as e:
                print(e)
                # Print any error messages to stdout
                return 'TLS-error: ' + str(e)

            finally:
                server.quit() # type: ignore

    return False


def email_compose(email: dict, att: str = '') -> MIMEMultipart:

    msg = MIMEMultipart('alternative')
    msg['Subject'] = email['subject']
    msg['From'] = email['from']
    msg['To'] = email['to']

    # Body of the  message (plain-text + HTML version)
    text = email['alt_body']
    html = email['body']

    # Convert the right MIME types (text/plain + text/html)
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message
    # RFC2046 - the last part of a multipart message is the best and preferred
    # We choose HTML version
    msg.attach(part1)
    msg.attach(part2)

    if type(att) is str and len(att) > 0:
        part3 = MIMEApplication(
            att,
            Name = 'deploy.log'
        )

        # After the file is closed
        part3['Content-Disposition'] = 'attachment; filename="deploy.log"'
        msg.attach(part3)

    return msg


def check_email(data_pass: dict = {}) -> dict:

    result = {
        'valid': False,
        'code': -1000,
        'code_type': str(type(-1000).__name__),
        'validator_message': 'check_email no_email',
        'description': 'Invalid response',
        'email': ''
    }

    if 'email' in data_pass.keys():
        
        result['validator_message'] = 'Validator library (pyIsEmail::is_email) warning'
        
        _is_email = is_email(str(data_pass['email']), allow_gtld=True, check_dns=False, diagnose=True)

        result['email'] = str(data_pass['email'])

        # print(type(_is_email), _is_email)
        if type(_is_email) is pyisemail.diagnosis.valid_diagnosis.ValidDiagnosis:
        
            result['valid'] = True if _is_email.code == 0 else False
            result['code'] = _is_email.code
            result['code_type'] = str(type(_is_email.code).__name__)
            result['validator_message'] = _is_email.message
            result['description'] = _is_email.description
            
    return result


def assign_template(template: str, data: dict) -> str:
    
    return f"email/{template}.html"
    """ 
    return render_template(
        f"email/{template}.html", data=data)
    """