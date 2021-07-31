"""SignTyp dataset."""
import re
from datetime import datetime

import requests
import tensorflow as tf
import tensorflow_datasets as tfds

from sign_language_datasets.datasets import SignDatasetConfig

_DESCRIPTION = """
SignTyp is a work in progress. We currently have over 20,000 videos for signers from Brazil, China, Croatia, Denmark, Egypt, Estonia, Ethiopia, France, Germany, Haiti, Honduras, Iraq, Italy,Lithuania, Nepal, Nicaragua, the Philippines, Portugal, Russia, Rwanda, Sri Lanka, Turkey, Uganda, the United States and Venezuela. We have complete sets of approximately 1000 video recordings each for China, Denmark, Egypt, Ethiopia, Haiti, Honduras, Iraq, Lithuania, Portugal,the Phillipines, Russia (2 signers), Turkey, and the United States. Clipping has been completed for all sets except a second Russian signer.

We currently have SignWriting transcriptions for approximately 9,000 signs, with more in progress. Each transcription includes detailed information on handshapes, orientation, actions, locations, as well as special sequencing and articulator relationship information. There is a downloadable file for all transcribed information for sign language researchers.

SignWriting transcription can be seen in our SignPuddles - see link below.

The project is sponsored by NSF (National Science Foundation) and is made possible by grant BCS-1049510 to the University of Connecticut and Harry van der Hulst.
"""

# TODO(SignTyp): BibTeX citation
_CITATION = """
"""


class SignTyp(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for SignTyp dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
        '1.0.0': 'Initial release.',
    }

    BUILDER_CONFIGS = [
        SignDatasetConfig(name="default", include_video=True, process_video=False)
    ]

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""

        features = {
            "id": tf.int32,
            "created_date": tfds.features.Text(),
            "modified_date": tfds.features.Text(),
            "sign_writing": tfds.features.Text(),
            "sign_language": tfds.features.Text(),
            "video": tfds.features.Text(),
        }

        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            features=tfds.features.FeaturesDict(features),
            homepage="https://signtyp.uconn.edu/",
            supervised_keys=None,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""

        cookies = {  # Cookies are mandatory, otherwise, doesn't download
            'PHPSESSID': 'r2oh4a7ork9se2bb03c52jcom7',
        }

        headers = {
            'Referer': 'https://signtyp.uconn.edu/signpuddle/export.php',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'If-None-Match': '"ks2Qn0SONVpb4uhxUcfjKipMmSo="',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://signtyp.uconn.edu',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        }

        data = {
            "ex_source": "All",
            "action": "Download",
        }

        res = requests.post('https://signtyp.uconn.edu/signpuddle/export.php',
                            data=data,
                            headers=headers,
                            cookies=cookies)

        spml = str(res.content)

        return {
            'train': self._generate_examples(spml),
        }

    def _generate_examples(self, spml):
        regex = '<entry id="(.*?)".*?cdt="(.*?)" mdt="(.*?)".*?term>(.*?)<.*?lxsg: (.*?)].*(http.*?)"'

        for row in spml.splitlines():
            datum = re.search(regex, row)

            if datum is not None:
                _id = datum.group(1)

                yield _id, {
                    "id": int(_id),
                    "created_date": str(datetime.fromtimestamp(int(datum.group(2)))),
                    "modified_date": str(datetime.fromtimestamp(int(datum.group(3)))),
                    "sign_writing": datum.group(4),
                    "sign_language": datum.group(5),
                    "video": datum.group(6),
                }
