"""
Key handling utilities for DSA keys.

These utilities depend on the :mod:`pyasn1` and :mod:`pyasn1_modules`.
"""

from pyasn1.codec.der import encoder, decoder
from pyasn1_modules.rfc3279 import Dss_Parms, DSAPublicKey

from . import biginteger
from ..constants import Attribute


def decode_dsa_domain_parameters(der):
    """
    Decode RFC 3279 DER-encoded Dss-Params.

    :param bytes der: DER-encoded parameters
    :rtype: dict(Attribute,*)
    """

    params, _ = decoder.decode(der, asn1Spec=Dss_Parms())

    return {
        Attribute.BASE: biginteger(params['g']),
        Attribute.PRIME: biginteger(params['p']),
        Attribute.SUBPRIME: biginteger(params['q']),
    }


def encode_dsa_domain_parameters(obj):
    """
    Encode RFC 3279 DER-encoded Dss-Params.

    :param DomainParameters obj: domain parameters
    :rtype: bytes
    """
    asn1 = Dss_Parms()
    asn1['g'] = int.from_bytes(obj[Attribute.BASE], byteorder='big')
    asn1['p'] = int.from_bytes(obj[Attribute.PRIME], byteorder='big')
    asn1['q'] = int.from_bytes(obj[Attribute.SUBPRIME], byteorder='big')

    return encoder.encode(asn1)