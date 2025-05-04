Introduction to ASN.1
=====================

ASN.1 is short for `Abstract Syntax Notation One`_.
It is a joint ISO/IEC and ITU-T standard  for
describing the syntax and encoding of data structures in a platform
independent way. The syntax of data structures in ASN.1 is described by a
syntax definiton language. This language is used to compose ever more
complex data types from a few simple ones such as integer and string. Often
you will see this language in other standards that define an application on
top of ASN.1 (for example LDAP). It is outside the scope of this
introduction to go any deeper into the ASN.1 syntax definition language.

The encoding of data structures in ASN.1 is defined by so-called
*encoding rules*. Not just one but many encoding rules
exist, and occasionally new ones are added. Each of the encoding rules is
powerful enough to encode any data type specified by the ASN.1 language.
Because of the multiple encoding rules, it also means that is it not enough
to know that a piece of data is ASN.1 to decode it: you also need to know
the encoding rules with which it was encoded.

ASN.1 was first conceived in 1984. Some people say it is old, other say it
is mature. Fact is that many Internet protocols are built on top of ASN.1.
Some of the most important of these protocols are:

* **LDAP** (Lightweight Directory Access Protocol)
* **Kerberos** (network authentication protocol
* **SNMP** (Simple Network Management Protocol)
* **X.509** (public key infrastructure, known from e.g. SSL certificates)

ASN.1 is not the only standard for defining the syntax and encoding of data
structures. Other standards are Sun's XDR_ (External Data Representation),
and EBNF_ (Extended Backus-Naur Form). XDR is used primarily for
ONC-RPC applications such as NFS (the Network File System). EBNF is perhaps
the most used standard of them all: HTTP and XML (and thereby all its
applications) are specified in EBNF.

ASN.1 Data Types or Tags
------------------------

ASN.1 data types are either primitive data types
such as integers and strings, or more complex ones built on them. Whatever
the details of the data type, each of them has the following properties.

* Its **number**.The number is a numerical identifier that
  identifies the data type uniquely amongst others in its class. For example,
  ASN.1 defines that the type ``integer`` has the number ``2``.

* Its **class**. Four classes exist:
  **universal**, **application**, **context**, **private**. Each class
  defines the scope of the data type, i.e. how broad is the type available.
  Universal types are always available while the other ones are more
  restricted.  All standard primitive types that are defined by ASN.1 are
  defined in the universal class.

* Its **encoding type** (or just **type**). Two
  types exist: **primitive** and **constructed**.
  Primitively types contain just one data
  value such as a number or a string, while constructed types contain a
  collection of other primitive or constructed types.

The three properties together (number, class, type) are also called the
**tag** of a data type.

ASN.1 Encoding
--------------

As mentioned above, the encoding of data structures is defined by ASN.1
encoding rules. The most well-known encodings rules are:

* **BER** (Basic Encoding Rules)
* **DER** (Distinguished Encoding Rules)

The BER and DER encodings are very similar: BER is a looser format and
sometimes allows a single value to be encoded in different ways. The DER is
a subset of BER and defines in case multiple encodings are possible which
one needs to be used. This means that a BER parser can read DER (because
that is just a special form of BER), and a DER generator automatically
generates valid BER (because all DER is also BER.)

**Python-ASN1** supports the DER and BER, and none of the other encoding rules.
The vast majority of applications use these encoding rules, so at the moment
no support for additional encoding rules is planned. When generating ASN.1,
**Python-ASN1** will output DER, while for parsing it supports BER. This
arrangement complies with the practise of being forgiving on input, and
strict on output.

The DER and BER encodings work according the the **TLV**
(Tag, Length, Value) principle. A stream of encoded ASN.1 data consists of a
sequence of zero or more (tags, lenght, value) tuples, one after the other.
These tuples are also called **records** in this manual,
although this is not a term that is defined in the ASN.1 standard. For each
data type, DER and BER define how to encode the tag (which we remember is a
combination of its number, class and type), the length (in octets) of the
data value, and the data value itself.

Because DER encoding results in a truly binary representation of the encoded
data, a format has been devised for being able to send these in an encoding of
printable characters so you can actually mail these things.

* **PEM** (Privacy Enhanced Mail) defined in RFC 1421.
  In essence PEM files are just base64 encoded versions of the DER encoded data.
  In order to distinguish from the outside what kind of data is inside the DER
  encoded string, a header and footer are present around the data.

References
----------

.. _ITU-T Study Group 17 - Languages for Telecommunication Systems:
.. _Abstract Syntax Notation One:
.. _ASN1: https://www.itu.int/en/ITU-T/studygroups/2017-2020/17/Pages/default.aspx

.. _External Data Representation Standard:
.. _XDR: https://datatracker.ietf.org/doc/html/rfc4506

.. _ISO\/IEC 14977\: Information technology -- Syntactic metalanguage -- Extended BNF:
.. _EBNF: https://standards.iso.org/ittf/PubliclyAvailableStandards/s026153_ISO_IEC_14977_1996(E).zip

* **ASN.1**
  `ITU-T Study Group 17 - Languages for Telecommunication Systems`_

* **XDR**
  `External Data Representation Standard`_

* **EBNF**
  `ISO\/IEC 14977\: Information technology -- Syntactic metalanguage -- Extended BNF`_
