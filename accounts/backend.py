from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
import ssl

class EmailBackend(DjangoEmailBackend):
    """
    Custom SMTP Email Backend for Python 3.12+ compatibility with older Django versions.
    Fixes: SMTP.starttls() got an unexpected keyword argument 'keyfile'
    """
    def open(self):
        if self.connection:
            return False
        
        try:
            # Call the standard open
            return super().open()
        except TypeError as e:
            if "unexpected keyword argument 'keyfile'" in str(e):
                # Manual implementation of open() without keyfile/certfile
                connection_params = {}
                if self.timeout is not None:
                    connection_params['timeout'] = self.timeout
                
                try:
                    self.connection = self.connection_class(self.host, self.port, **connection_params)
                    
                    # Receive the greeting from the server.
                    self.connection.ehlo()
                    
                    if self.use_tls:
                        # Call starttls WITHOUT keyfile and certfile
                        self.connection.starttls()
                        self.connection.ehlo()
                    
                    if self.username and self.password:
                        try:
                            self.connection.login(self.username, self.password)
                        except smtplib.SMTPAuthenticationError as e:
                            # Provide a more helpful error message for BadCredentials
                            if 'BadCredentials' in str(e) or '535' in str(e):
                                raise Exception(
                                    "SMTP Authentication Failed (Bad Credentials). "
                                    "Please ensure you are using a valid 'App Password' for Gmail/Google Workspace. "
                                    "Go to: https://myaccount.google.com/apppasswords to generate a new one."
                                ) from e
                            raise
                    
                    return True
                except Exception as e:
                    if self.fail_silently:
                        return False
                    # Print or log the error to server console for easier debugging
                    print(f"EMAIL ERROR: {str(e)}")
                    raise
            raise
