import unittest
from unittest.mock import MagicMock
from gdmo import DbxMassEmail
from unittest.mock import MagicMock, patch

class TestDbxMassEmail(unittest.TestCase):

    @patch('gdmo.dbx.dbxmassemail.smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        dbx_mass_email = DbxMassEmail(smtpserver='smtp.example.com')
        recipients = ['recipient1@example.com', 'recipient2@example.com']
        dbx_mass_email.set_recipients(recipients)
        dbx_mass_email.set_subject('Test Subject for the emailer')
        dbx_mass_email.set_body('This is the body of the email. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')
        dbx_mass_email.set_mail_summary('Test Summary with Lorem Ipsum')

        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail = MagicMock()

        result = dbx_mass_email.send_email()

        self.assertEqual(mock_smtp_instance.sendmail.call_count, len(recipients))
        self.assertEqual(result['Success'][0], len(recipients))  # All emails succeed
        self.assertEqual(result['Failed'][0], 0)  # No failures

    def test_set_and_get_recipients(self):
        dbx_mass_email = DbxMassEmail(smtpserver='smtp.example.com')
        recipients = ['recipient1@example.com', 'recipient2@example.com']
        dbx_mass_email.set_recipients(recipients)
        self.assertEqual(dbx_mass_email.get_recipients(), recipients)

    def test_set_and_get_subject(self):
        dbx_mass_email = DbxMassEmail(smtpserver='smtp.example.com')
        subject = 'Test Subject'
        dbx_mass_email.set_subject(subject)
        self.assertEqual(dbx_mass_email.get_subject(), subject)

    def test_set_and_get_body(self):
        dbx_mass_email = DbxMassEmail(smtpserver='smtp.example.com')
        body = 'This is the body of the email. This is the body of the email. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        dbx_mass_email.set_body(body)
        self.assertEqual(dbx_mass_email.get_body(), body)

    def test_set_and_get_mail_summary(self):
        dbx_mass_email = DbxMassEmail(smtpserver='smtp.example.com')
        summary = 'Test Summary'
        dbx_mass_email.set_mail_summary(summary)
        self.assertEqual(dbx_mass_email.get_mail_summary(), summary)

if __name__ == '__main__':
    unittest.main()