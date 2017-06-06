"""
PKCS#11 RSA Public Key Cryptography
"""

import pkcs11
from pkcs11 import Attribute, KeyType, ObjectClass, Mechanism, MGF

from . import TestCase, Not


class RSATests(TestCase):

    def setUp(self):
        super().setUp()

        self.public, self.private = \
            self.session.generate_keypair(KeyType.RSA, 1024)

    def test_sign(self):
        data = b'HELLO WORLD' * 1024

        signature = self.private.sign(data)
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertTrue(self.public.verify(data, signature))
        self.assertFalse(self.public.verify(data, b'1234'))

    def test_sign_stream(self):
        data = (
            b'I' * 16,
            b'N' * 16,
            b'P' * 16,
            b'U' * 16,
            b'T' * 10,  # don't align to the blocksize
        )

        signature = self.private.sign(data)
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertTrue(self.public.verify(data, signature))

    def test_key_wrap(self):
        key = self.session.generate_key(KeyType.AES, 128,
                                        template={
                                            Attribute.EXTRACTABLE: True,
                                            Attribute.SENSITIVE: False,
                                        })

        data = self.public.wrap_key(key)
        self.assertNotEqual(data, key[Attribute.VALUE])

        key2 = self.private.unwrap_key(ObjectClass.SECRET_KEY,
                                       KeyType.AES,
                                       data,
                                       template={
                                               Attribute.EXTRACTABLE: True,
                                               Attribute.SENSITIVE: False,
                                       })

        self.assertEqual(key[Attribute.VALUE], key2[Attribute.VALUE])

    def test_encrypt_oaep(self):
        data = b'SOME DATA'

        crypttext = self.public.encrypt(data,
                                        mechanism=Mechanism.RSA_PKCS_OAEP,
                                        mechanism_param=(Mechanism.SHA_1,
                                                         MGF.SHA1,
                                                         None))

        self.assertNotEqual(data, crypttext)

        plaintext = self.private.decrypt(crypttext,
                                         mechanism=Mechanism.RSA_PKCS_OAEP,
                                         mechanism_param=(Mechanism.SHA_1,
                                                          MGF.SHA1,
                                                          None))

        self.assertEqual(data, plaintext)

    @Not.softhsm2
    def test_sign_pss(self):
        data = b'SOME DATA'

        # These are the default params
        signature = self.private.sign(data,
                                      mechanism=Mechanism.SHA1_RSA_PKCS_PSS,
                                      mechanism_param=(Mechanism.SHA_1,
                                                       MGF.SHA1,
                                                       20))

        self.assertTrue(self.public.verify(
            data, signature, mechanism=Mechanism.SHA1_RSA_PKCS_PSS))

    def test_encrypt_too_much_data(self):
        data = b'1234' * 128

        # You can't encrypt lots of data with RSA
        # This should ideally throw DataLen but you can't trust it
        with self.assertRaises(pkcs11.PKCS11Error):
            self.public.encrypt(data)
