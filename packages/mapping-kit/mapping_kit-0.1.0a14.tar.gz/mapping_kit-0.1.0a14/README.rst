.. |package-name| replace:: mapping-kit

.. |pypi-version| image:: https://img.shields.io/pypi/v/mapping-kit?label=PyPI%20Version&color=4BC51D
   :alt: PyPI Version
   :target: https://pypi.org/projects/mapping-kit/

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/mapping-kit?label=PyPI%20Downloads&color=037585
   :alt: PyPI Downloads
   :target: https://pypi.org/projects/mapping-kit/

mapping-kit
###########

|pypi-version| |pypi-downloads|

Description
***********

Provides
 - AttributeDict (keys accessible as dot-denoted attributes, remains subscriptable)
 - GroupDict (groups keys based on prefix, makes it easy to write complex configuration in a single dictionary and access it easily)
 - SuperDict (a dictionary that is defaultdict, OrderedDict, case-insensitive, and recursive, each customizable by user; also stores ancestry for each item)
 - NestedDict (nests paremeters )
 - VirtualIterable (iterate through multilpe objects without creating concrete objects)


Examples of AttributeDict:

.. code-block:: python

   from mapping_kit import AttributeDict

   # All the standard ways that a Python dict can be created in, can be used to
   # create AttributeDict. It can also be used as a normal dictionary.

   sample_dict = {
       "first_name": "Charlie",
       "last_name": "Brown",
   }
   ad_from_dict = AttributeDict(**sample_dict)
   print("Hello", ad_from_dict.first_name, ad_from_dict["last_name"])
   # Hello Charlie Brown

   sample_tuples = [
       ("model", "Hindustan Ambassador"),
       ("production", "1957-2014"),
   ]
   ad_from_tuples = AttributeDict(sample_tuples)
   print(ad_from_tuples.model, "- production years", ad_from_tuples["production"])
   # Hindustan Ambassador - production years 1957-2014


Examples of CartesianIterator:

.. code-block:: python

   from mapping_kit import CartesianIterator

   ci = CartesianIterator(["some", "no"],
                          ["one", "two"],
                          ["saw", "took", "did"],
                          ["it"])
   for cartesian in ci:
       print(cartesian)

   # ['some', 'one', 'saw', 'it']
   # ['some', 'one', 'took', 'it']
   # ['some', 'one', 'did', 'it']
   # ['some', 'two', 'saw', 'it']
   # ['some', 'two', 'took', 'it']
   # ['some', 'two', 'did', 'it']
   # ['no', 'one', 'saw', 'it']
   # ['no', 'one', 'took', 'it']
   # ['no', 'one', 'did', 'it']
   # ['no', 'two', 'saw', 'it']
   # ['no', 'two', 'took', 'it']
   # ['no', 'two', 'did', 'it']


Examples of GroupDict:

.. code-block:: python

   from mapping_kit import GroupDict

   sample = {
       "#Version": "1.4.9a1",
       "beverages": {
           "_lassi": "A yoghurt based beverage",
           "_aamras": "Thick mango pulp",
           "*jaljeera": "Spices mixed in water, out of stock",
           "*alcoholic_drinks": {
               "beer": "4-6% alcohol",
               "red_wine": "5.5-10% alcohol",
           },
       },
       "appetizers": {
           "_pani_puri": "Masala water filled crispy puffed bread",
           "!chicken_pakora": "Deep-fried chicken stuffing in Indian pakoras",
           "_aloo_chaat": "Potato with spicy gravy",
           "!prawn_toast": "Sesame and prawns rolled in bread",
       }
   }

   gd = GroupDict(sample,
                  grouping={"#": "comment",  # arbitrary group names
                            "_": "vegetarian",
                            "!": "non_vegetarian",
                            "*": "not_available"},
                  default_group_name="public",
                  key_ignorecase=True)

   # Accessing group `comment`
   print("The version is", gd.comment["version"])
   # The version is 1.4.9a1

   for key, value in gd.comment.items():
       print(f"{key}: {value}")
   # Version: 1.4.9a1

   # Chained groups
   veg_appetizers = gd.public["appetizers"].vegetarian
   print("Vegetarian appetizers are:")
   for key in veg_appetizers.keys():
       print(f"  {key}")
   # Vegetarian appetizers are:
   #   pani_puri
   #   aloo_chaat

   beverages_not_available = gd["beverages"].not_available
   print("Beverages not available are:")
   for bna, bna_desc in beverages_not_available.items():
       if isinstance(bna_desc, dict):
           for bna_sub, bna_sub_desc in bna_desc.public.items():
               print(f"  {bna_sub} ({bna_sub_desc})")
       else:
           print(f"  {bna} ({bna_desc})")
   # Beverages not available are:
   #   jaljeera (Spices mixed in water, out of stock)
   #   beer (4-6% alcohol)
   #   red_wine (5.5-10% alcohol)


Examples of NestedDict:

.. code-block:: python

   from mapping_kit import NestedDict

   sample = {
       "in": {
           "support-conf": {
               "contact-email": "in@example.com",
               "contact-call": "+91-99999-88888",
           },
           "official-name": "Republic of India",
           "states": {
               "ka": {
                   "support-conf": {
                       "contact-email": "in-ka@example.com",
                   },
                   "name": "Karnataka",
                   "cities": {
                       "blr": {
                           "description": "Bengaluru Urban",
                           "support-conf": {
                               "contact-call": "+91-77777-66666",
                           },
                       },
                   },
               },
           },
       },
   }

   nd = NestedDict(sample, nest_keys=["support-conf"])

   blr_conf = nd["in"]["states"]["ka"]["cities"]["blr"]["support-conf"]
   for key, value in blr_conf.items():
       print(key, ": ",  value, sep="")
   # contact-call: +91-77777-66666
   # contact-email: in-ka@example.com

   ka_conf = nd["in"]["states"]["ka"]["support-conf"]
   for key, value in ka_conf.items():
       print(key, ": ",  value, sep="")
   # contact-email: in-ka@example.com
   # contact-call: +91-99999-88888

   in_conf = nd["in"]["support-conf"]
   for key, value in in_conf.items():
       print(key, ": ",  value, sep="")
   # contact-email: in@example.com
   # contact-call: +91-99999-88888

   nd.disable_ancestry_lookup()                     # temporarily disable lookup
   nd.enable_ancestry_lookup()                      # enable back lookup


Examples of SuperDict:

.. code-block:: python

   from mapping_kit import SuperDict

   sample = {
       "mode": "read",
       "max-size": 1024 * 1024,
       "type": "csv",
       "files": {
           "mode": "append",
           "file-1": {
               "mode": "write",
               "Name": "FromMumbai.pdf",
           },
           "file-2": {
               "max-size": 3 * 1024 * 1024,
               "Name": "FromTokyo.pdf",
               "worksheet": {
                   "rates": "week-1",
               },
           },
       },
   }

   sd = SuperDict(sample,
                  key_ignorecase=True,
                  # ordereddict=True,
                  # default_factory=list,
                  )
   # ordereddict: makes order of keys important when comparing two SuperDicts
   # default_factory: same usage as in collections.defaultdict

   file_1 = sd["files"]["file-1"]
   file_2 = sd["files"]["file-2"]
   worksheet = file_2["worksheet"]

   for k, v in file_2.items():
       print(f"file-2: {k}={v}")
   # file-2: max-size=3145728
   # file-2: name=FromTokyo.pdf              (`name` instead of `Name`)
   # file-2: worksheet=SuperDict(...)        (recursive SuperDict)
   # file-2: mode=append                     (inherited from nearest ancestry)

   print(f"file-1: NAME={file_1["NAME"]}")
   # file-1: NAME=FromMumbai.pdf             (case-insensitive key `NAME`)

   print(f"file-1.parent: mode={file_1.parent["mode"]}")
   # file-1.parent: mode=append              (access parent)

   print(f"worksheet.parent.parent: mode={worksheet.parent.parent["mode"]}")
   # worksheet.parent.parent: mode=append    (access parent hierarchy)

   print(f"worksheet.root: mode={worksheet.root["mode"]}")
   # worksheet.root: mode=read               (jump straight to root)

   print(f"worksheet.root['files']: mode={worksheet.root["files"]["mode"]}")
   # worksheet.root['files']: mode=append    (access keys within root)


Example of VirtualIterable:

.. code-block:: python

   from mapping_kit import VirtualIterable

   for item in VirtualIterable(["a", "b"], None, 4, "c" (1, 2)):
       print(item)
   # a
   # b
   # None
   # 4
   # c
   # 1
   # 2


Note: This is an alpha version, and things may change quite a bit.