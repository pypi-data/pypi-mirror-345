import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class DbxEmailer:
    """
    A utility class for interacting with Databricks widgets to read and create widget values.

    Usage:
    - To read the value from an existing widget:
        value = DbxWidget(dbutils, widget_name)

    - To create a new widget with specified type and options:
        value = DbxWidget(dbutils, widget_name, type='dropdown', defaultValue='Red', choices=["Red", "Blue", "Yellow"])

    Inputs:
    - dbutils: Databricks utility object for widget operations
    - name: Name of the widget
    - type: Type of the widget (text, dropdown, multiselect, combobox). Defaults to Text if not provided
    - defaultValue: Default value for the widget. Defaults to blank
    - **kwargs: Additional keyword arguments for widget creation

    Example:
    - Existing method:
        dbutils.widgets.dropdown("colour", "Red", "Enter Colour", ["Red", "Blue", "Yellow"])
        colour = dbutils.widgets.read("colour")

    - New method:
        colour = DbxWidget(dbutils, "colour", 'dropdown', "Red", choices=["Red", "Blue", "Yellow"])
    """

    def __new__(self, smtpserver, subject, body, toaddr, fromaddr, ccaddr='', priority='3', timeout=10, bccaddr=''):
        """
            Sends an email with or without attachment from Databricks.

            Args:
                smtpserver (str): SMTP Server to connect to
                subject (str): Email subject
                body (str): Regular or HTML string body content of the email
                toaddr (str): Comma-separated string of email addresses to send to
                ccaddr (str, optional): Comma-separated string of email addresses to CC
                fromaddr (str, optional): Email address to send from
                priority (str, optional): Priority level of the email (1 to 5)
                timeout (int, optional): Timeout value for server connection
                bccaddr (str, optional): Comma-separated string of email addresses to BCC
        """  
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        toaddr = toaddr.split(',')
        msg['To'] = ", ".join(toaddr)

        if ccaddr:
            ccaddr = ccaddr.split(',')
            msg['Cc'] = ", ".join(ccaddr)
            toaddr = toaddr + ccaddr

        if bccaddr:
            bccaddr = bccaddr.split(',')
            msg['Bcc'] = ", ".join(bccaddr)
            toaddr = toaddr + bccaddr


        msg['Subject'] = subject
        body = body
        msg.attach(MIMEText(body, 'html'))
        msg['X-Priority'] = priority

        server_connect = False
        server_connect_attempts = 0
        
        # Try 5 times to connect to server
        # Usually results in a TIMEOUT, so we had to try several times for it to secure a connection.
        while server_connect == False and server_connect_attempts < 20:
            try: 
                server_connect_attempts += 1
                server = smtplib.SMTP(smtpserver, timeout=timeout)
                server.ehlo()
                #server.starttls()    #For Some reason, this property started to fail...
                server_connect = True
            except:
                pass
            
        # If we have a secure connection, email will be sent.
        if server_connect: 
            try:
                server.sendmail(fromaddr, toaddr, msg.as_string()) # email sent.
                #print(f'\t*****Email sent after {server_connect_attempts} server connection attempts*****')
            except Exception as e:
                raise Exception(f'Error occured when trying to send the email: {e}')
            finally:
                server.quit() # closing connection 
                print(f'Email {subject} succesfully sent to {toaddr}')
        else:
            raise TimeoutError # Couldn't establish a connection, raise TimeoutError