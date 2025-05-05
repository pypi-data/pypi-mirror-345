import os
import sys
import unittest
import logging

base_path = os.path.realpath(os.path.dirname(__file__))
root = os.path.join(base_path, '..')
sys.path.append(root)
from mailparser_reply import EmailReplyParser
from mailparser_reply.constants import MAIL_LANGUAGE_DEFAULT


class EmailMessageTest(unittest.TestCase):
    def test_david1_simple(self):
        mail = self.get_email('delete1', parse=True, languages=['en', 'de', 'david'])
        self.assertTrue("Original Message processed by david" not in mail.latest_reply)
        self.assertTrue("Original Message processed by david" not in mail.replies[0].content)
        self.assertTrue("Original Message processed by david" in mail.replies[1].content)

    def test_david2_simple(self):
        mail = self.get_email('delete2', parse=True, languages=['en', 'de', 'david'])
        self.assertTrue("Original Message processed by david" not in mail.latest_reply)
        self.assertTrue("Original Message processed by david" not in mail.replies[0].content)
        self.assertTrue("Original Message processed by david" in mail.replies[1].content)

    def test_david3_link_header(self):
        mail = self.get_email('delete3', parse=True, languages=['en', 'de', 'david'])
        self.assertTrue("Original Message processed by david" not in mail.latest_reply)
        self.assertTrue(mail.latest_reply.strip() == 'Test hello darkness')
        self.assertTrue("Original Message processed by david" not in mail.replies[0].content)
        self.assertTrue("Original Message processed by david" in mail.replies[1].content)

    def test_david4_link_header(self):
        mail = self.get_email('delete4', parse=True, languages=['en', 'de', 'david'])
        self.assertTrue("Original Message processed by david" not in mail.latest_reply)
        self.assertTrue(mail.latest_reply.strip() == 'Test hello darkness')
        self.assertTrue("Original Message processed by david" not in mail.replies[0].content)
        self.assertTrue("Original Message processed by david" in mail.replies[1].content)

    def test_david8_quoted_link_header(self):
        mail = self.get_email('delete8', parse=True, languages=['en', 'de', 'david'])

        self.assertTrue("Original Message processed by david" not in mail.latest_reply)
        self.assertTrue("Original Message processed by david" not in mail.replies[0].content)
        self.assertTrue("Original Message processed by david" in mail.replies[1].content)

    def get_email(self, name: str, parse: bool = True, languages: list = None):
        """ Return EmailMessage instance or text content """
        with open(f'test/advanced/{name}.txt') as f:
            text = f.read()
        return EmailReplyParser(
            languages=languages or [MAIL_LANGUAGE_DEFAULT]
        ).read(text) if parse else text


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    unittest.main()


# ensures all of these regex-es are matching:

"""
Original Message processed by david®
Original Message processed by david®<https://david.tobit.software>
 Original Message processed by david®
[Original Message processed by david®](https://david.tobit.software)
 [Original Message processed by david®](https://david.tobit.software)

> Original Message processed by david®
> Original Message processed by david®<https://david.tobit.software>
>> [Original Message processed by david®](https://david.tobit.software)
> > [Original Message processed by david®](https://david.tobit.software)

> [Original Message processed by david®](https://david.tobit.software)
> **[#RMJ-12345] foobar 2. September 2024, 12:53 Uhr
> **Von** [RAUSYS](mailto:foo@bar.com)
> **An** [RAUSYS-2](mailto:bar@foo.de)
"""
